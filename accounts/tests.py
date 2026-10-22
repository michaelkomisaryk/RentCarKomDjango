from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from accounts.models import Role, User
from fleet.models import Car
from rentals.models import Rental
from rentals.services import create_rental


class UserAccountTests(TestCase):
    def test_email_login_stores_a_hashed_password(self):
        user = User.objects.create_user(
            email="Client@Example.com",
            password="secret1",
            name="Client",
        )

        self.assertEqual(user.email, "client@example.com")
        self.assertEqual(user.role, Role.CLIENT)
        self.assertNotEqual(user.password, "secret1")
        self.assertTrue(user.check_password("secret1"))

    def test_seed_users_can_sign_in_with_the_original_passwords(self):
        call_command("seed_users")

        admin = User.objects.get(email="admin@rentcarkom.com")
        manager = User.objects.get(email="manager@rentcarkom.com")
        self.assertEqual(admin.role, Role.ADMIN)
        self.assertEqual(manager.role, Role.MANAGER)
        self.assertTrue(admin.check_password("admin123"))
        self.assertTrue(manager.check_password("manager123"))
        self.assertNotEqual(admin.password, "admin123")


class AuthScreenTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_users")

    def test_login_logout_and_rejected_password(self):
        bad = self.client.post(
            reverse("accounts:login"),
            {"username": "admin@rentcarkom.com", "password": "nope"},
        )
        self.assertContains(bad, "Invalid email or password")

        empty = self.client.post(reverse("accounts:login"), {"username": "", "password": ""})
        self.assertContains(empty, "Please fill in all fields")

        ok = self.client.post(
            reverse("accounts:login"),
            {"username": "Admin@RentCarKom.com", "password": "admin123"},
        )
        self.assertRedirects(ok, reverse("fleet:catalog"))

        page = self.client.get(reverse("fleet:catalog"))
        self.assertContains(page, "ADMIN")
        self.assertContains(page, "All Rentals")
        self.assertContains(page, "Add Car")

        self.client.post(reverse("accounts:logout"))
        guest = self.client.get(reverse("fleet:catalog"))
        self.assertContains(guest, "GUEST")
        self.assertContains(guest, "Sign in")
        self.assertNotContains(guest, "All Rentals")

    def test_registration_creates_a_client(self):
        created = self.client.post(
            reverse("accounts:register"),
            {
                "name": "New Client",
                "email": "New@Example.com",
                "password": "secret1",
                "phone": "0671234567",
                "rnokpp": "1234567890",
                "driver_license": "кіа654321",
            },
            follow=True,
        )
        self.assertContains(created, "Registered! Please sign in.")
        user = User.objects.get(email="new@example.com")
        self.assertEqual(user.role, Role.CLIENT)
        self.assertEqual(user.name, "New Client")
        self.assertEqual(user.phone, "+380671234567")
        self.assertEqual(user.rnokpp, "1234567890")
        self.assertEqual(user.driver_license, "КІА 654321")

        duplicate = self.client.post(
            reverse("accounts:register"),
            {
                "name": "New Client",
                "email": "new@example.com",
                "password": "secret1",
                "phone": "0671234567",
                "rnokpp": "1234567890",
                "driver_license": "ВХА 123456",
            },
        )
        self.assertContains(duplicate, "Email already registered")

        short = self.client.post(
            reverse("accounts:register"),
            {
                "name": "Short",
                "email": "short@example.com",
                "password": "123",
                "phone": "0671234567",
                "rnokpp": "1234567890",
                "driver_license": "ВХА 123456",
            },
        )
        self.assertContains(short, "Password must be at least 6 characters")

        self.client.login(email="new@example.com", password="secret1")
        page = self.client.get(reverse("fleet:catalog"))
        self.assertContains(page, "CLIENT")
        self.assertNotContains(page, "All Rentals")
        self.assertNotContains(page, "Add Car")

    def test_manager_menu_includes_rentals_only(self):
        self.client.login(email="manager@rentcarkom.com", password="manager123")
        page = self.client.get(reverse("fleet:catalog"))
        self.assertContains(page, "MANAGER")
        self.assertContains(page, "All Rentals")
        self.assertNotContains(page, "Add Car")


class ProfileTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_cars")
        cls.client_user = User.objects.create_user(
            email="ada@example.com",
            password="secret1",
            name="Ada Lovelace",
            phone="+380671234567",
            rnokpp="1234567890",
            driver_license="ВХА 123456",
        )

    def test_guest_is_sent_to_login(self):
        response = self.client.get(reverse("accounts:profile"))
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:profile')}",
            fetch_redirect_response=False,
        )

    def test_profile_shows_the_rented_car(self):
        car = Car.objects.get(plate="KA 2401 IK")
        create_rental(car, self.client_user, 3, self.client_user.name)
        self.client.force_login(self.client_user)

        page = self.client.get(reverse("accounts:profile"))

        self.assertContains(page, "Ada Lovelace")
        self.assertContains(page, "ada@example.com")
        self.assertContains(page, "Toyota Yaris")
        self.assertContains(page, "KA 2401 IK")

    def test_booking_takes_the_name_from_the_profile(self):
        car = Car.objects.get(plate="BB 5678 KK")
        self.client.force_login(self.client_user)

        self.client.post(reverse("rentals:rent_car", args=[car.pk]), {"days": 2})

        rental = Rental.objects.get(car=car)
        self.assertEqual(rental.renter_name, "Ada Lovelace")
        self.assertEqual(rental.user_email, "ada@example.com")
        self.assertEqual(rental.renter_phone, "+380671234567")
        self.assertEqual(rental.renter_rnokpp, "1234567890")
        self.assertEqual(rental.renter_license, "ВХА 123456")

    def test_profile_changes_the_password_and_keeps_the_session(self):
        self.client.force_login(self.client_user)
        wrong = self.client.post(
            reverse("accounts:profile"),
            {
                "form": "password",
                "current_password": "nope",
                "new_password": "newsecret",
                "confirm_password": "newsecret",
            },
        )
        self.assertContains(wrong, "Current password is incorrect")

        mismatch = self.client.post(
            reverse("accounts:profile"),
            {
                "form": "password",
                "current_password": "secret1",
                "new_password": "newsecret",
                "confirm_password": "other",
            },
        )
        self.assertContains(mismatch, "Passwords do not match")

        changed = self.client.post(
            reverse("accounts:profile"),
            {
                "form": "password",
                "current_password": "secret1",
                "new_password": "newsecret",
                "confirm_password": "newsecret",
            },
            follow=True,
        )
        self.assertContains(changed, "Password changed.")
        self.assertContains(changed, "Ada Lovelace")
        self.client_user.refresh_from_db()
        self.assertTrue(self.client_user.check_password("newsecret"))
        self.assertFalse(self.client_user.check_password("secret1"))
