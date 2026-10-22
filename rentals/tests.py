from datetime import date, datetime, time

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Role, User
from fleet.models import Car
from rentals.models import Rental
from rentals.services import RentalError, create_rental, rental_end


def make_user(email, role):
    return User.objects.create_user(
        email=email,
        password="secret1",
        name="Renter",
        role=role,
        phone="+380671112233",
        rnokpp="1234567890",
        driver_license="ВХА 123456",
    )


class RentalCalendarTests(TestCase):
    def test_end_date_crosses_a_month_boundary(self):
        start = timezone.make_aware(datetime(2026, 1, 30, 10, 0, 0))
        end = timezone.localtime(rental_end(start, 5))

        self.assertEqual(end.date(), date(2026, 2, 3))
        self.assertEqual(end.time(), time(23, 59, 59))


class RentalFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_cars")
        cls.client_user = make_user("client-rent@example.com", Role.CLIENT)
        cls.manager = make_user("manager-rent@example.com", Role.MANAGER)
        cls.other = make_user("other-rent@example.com", Role.CLIENT)

    def setUp(self):
        self.car = Car.objects.get(plate="KA 2401 IK")

    def test_guest_cannot_rent_and_client_cannot_open_the_desk(self):
        guest = self.client.post(reverse("rentals:rent_car", args=[self.car.pk]), {"days": 2, "renter_name": "Guest"})
        self.assertRedirects(
            guest,
            f"{reverse('accounts:login')}?next={reverse('rentals:rent_car', args=[self.car.pk])}",
            fetch_redirect_response=False,
        )
        self.assertEqual(Rental.objects.count(), 0)

        self.client.force_login(self.client_user)
        denied = self.client.get(reverse("rentals:rental_list"))
        self.assertEqual(denied.status_code, 403)

    def test_active_rental_blocks_a_second_booking(self):
        self.client.force_login(self.client_user)
        first = self.client.post(
            reverse("rentals:rent_car", args=[self.car.pk]),
            {"days": 3, "renter_name": "Ada"},
            follow=True,
        )
        rental = Rental.objects.get()
        self.assertEqual(rental.days, 3)
        self.assertEqual(rental.total_price, self.car.price * 3)
        self.assertEqual(rental.car_plate, "KA 2401 IK")
        self.assertContains(first, "Rental confirmed")

        self.car.price = 999
        self.car.save(update_fields=["price"])

        self.client.force_login(self.other)
        second = self.client.post(
            reverse("rentals:rent_car", args=[self.car.pk]),
            {"days": 1, "renter_name": "Grace"},
            follow=True,
        )
        self.assertContains(second, "Car is already rented")
        self.assertEqual(Rental.objects.filter(status=Rental.Status.ACTIVE).count(), 1)
        rental.refresh_from_db()
        self.assertEqual(rental.price_per_day, 28)

        available = self.client.get(reverse("fleet:catalog"), {"available": "1"})
        plates = [car.plate for car in available.context["cars"]]
        self.assertNotIn("KA 2401 IK", plates)
        self.assertEqual(len(plates), 39)

    def test_manager_completes_a_rental_and_the_car_can_be_booked_again(self):
        rental = create_rental(self.car, self.client_user, 2, "Ada")
        self.client.force_login(self.client_user)
        self.assertEqual(
            self.client.post(reverse("rentals:rental_complete", args=[rental.pk])).status_code,
            403,
        )

        self.client.force_login(self.manager)
        home = self.client.get(reverse("fleet:catalog"))
        self.assertEqual(home.context["stats"]["total_cars"], 40)
        self.assertEqual(home.context["stats"]["rented"], 1)
        self.assertEqual(home.context["stats"]["available"], 39)
        self.assertEqual(home.context["stats"]["all_rentals"], 1)
        desk = self.client.get(reverse("rentals:rental_list"))
        self.assertContains(desk, "KA 2401 IK")

        done = self.client.post(reverse("rentals:rental_complete", args=[rental.pk]), follow=True)
        self.assertContains(done, "Rental completed")
        rental.refresh_from_db()
        self.assertEqual(rental.status, Rental.Status.COMPLETED)
        self.car.refresh_from_db()
        self.assertFalse(self.car.is_rented)

        self.client.force_login(self.other)
        again = self.client.post(
            reverse("rentals:rent_car", args=[self.car.pk]),
            {"days": 1, "renter_name": "Grace"},
        )
        self.assertRedirects(again, reverse("fleet:catalog"))
        self.assertEqual(Rental.objects.filter(status=Rental.Status.ACTIVE).count(), 1)

    def test_admin_can_cancel_and_a_short_rental_is_rejected(self):
        admin = make_user("admin-rent@example.com", Role.ADMIN)
        rental = create_rental(self.car, self.client_user, 4, "Ada")
        self.client.force_login(admin)
        response = self.client.post(
            reverse("rentals:rental_cancel", args=[rental.pk]),
            {"next": reverse("fleet:car_detail", args=[self.car.pk])},
            follow=True,
        )
        self.assertContains(response, "Rental cancelled")
        self.assertContains(response, "Available for Rent")
        rental.refresh_from_db()
        self.assertEqual(rental.status, Rental.Status.CANCELLED)

        self.client.force_login(self.client_user)
        rejected = self.client.post(
            reverse("rentals:rent_car", args=[self.car.pk]),
            {"days": 0, "renter_name": ""},
            follow=True,
        )
        self.assertContains(rejected, "Enter at least 1 day")

        with self.assertRaises(RentalError):
            create_rental(self.car, self.client_user, 1, "   ")

    def test_client_can_cancel_only_their_own_rental(self):
        rental = create_rental(self.car, self.client_user, 2, "Renter")
        self.client.force_login(self.other)
        missing = self.client.post(reverse("rentals:rental_cancel_own", args=[rental.pk]))
        self.assertEqual(missing.status_code, 404)
        rental.refresh_from_db()
        self.assertEqual(rental.status, Rental.Status.ACTIVE)

        self.client.force_login(self.client_user)
        page = self.client.get(reverse("accounts:profile"))
        self.assertContains(page, "Cancel rental")
        done = self.client.post(reverse("rentals:rental_cancel_own", args=[rental.pk]), follow=True)
        self.assertContains(done, "Rental cancelled")
        rental.refresh_from_db()
        self.assertEqual(rental.status, Rental.Status.CANCELLED)
        self.car.refresh_from_db()
        self.assertFalse(self.car.is_rented)
