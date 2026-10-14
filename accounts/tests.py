from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from accounts.models import Role, User


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
            reverse("login"),
            {"username": "admin@rentcarkom.com", "password": "nope"},
        )
        self.assertContains(bad, "Invalid email or password")

        empty = self.client.post(reverse("login"), {"username": "", "password": ""})
        self.assertContains(empty, "Please fill in all fields")

        ok = self.client.post(
            reverse("login"),
            {"username": "Admin@RentCarKom.com", "password": "admin123"},
        )
        self.assertRedirects(ok, reverse("catalog"))

        page = self.client.get(reverse("catalog"))
        self.assertContains(page, "ADMIN")
        self.assertContains(page, "All Rentals")
        self.assertContains(page, "Add Car")

        self.client.post(reverse("logout"))
        guest = self.client.get(reverse("catalog"))
        self.assertContains(guest, "GUEST")
        self.assertContains(guest, "Sign in")
        self.assertNotContains(guest, "All Rentals")

    def test_registration_creates_a_client(self):
        created = self.client.post(
            reverse("register"),
            {"name": "New Client", "email": "New@Example.com", "password": "secret1"},
            follow=True,
        )
        self.assertContains(created, "Registered! Please sign in.")
        user = User.objects.get(email="new@example.com")
        self.assertEqual(user.role, Role.CLIENT)
        self.assertEqual(user.name, "New Client")

        duplicate = self.client.post(
            reverse("register"),
            {"name": "New Client", "email": "new@example.com", "password": "secret1"},
        )
        self.assertContains(duplicate, "Email already registered")

        short = self.client.post(
            reverse("register"),
            {"name": "Short", "email": "short@example.com", "password": "123"},
        )
        self.assertContains(short, "Password must be at least 6 characters")

        self.client.login(email="new@example.com", password="secret1")
        page = self.client.get(reverse("catalog"))
        self.assertContains(page, "CLIENT")
        self.assertNotContains(page, "All Rentals")
        self.assertNotContains(page, "Add Car")

    def test_manager_menu_includes_rentals_only(self):
        self.client.login(email="manager@rentcarkom.com", password="manager123")
        page = self.client.get(reverse("catalog"))
        self.assertContains(page, "MANAGER")
        self.assertContains(page, "All Rentals")
        self.assertNotContains(page, "Add Car")
