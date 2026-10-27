import time

from django.core.management import call_command
from selenium.webdriver.common.by import By

from accounts.chrome import ChromeCase
from accounts.models import Role
from fleet.models import Car
from rentals.models import Rental
from rentals.tests import make_user


class BookingChromeTests(ChromeCase):
    def prepare(self):
        call_command("seed_cars")
        self.client_user = make_user("client-chrome@example.com", Role.CLIENT)
        self.other = make_user("other-chrome@example.com", Role.CLIENT)
        self.car = Car.objects.get(plate="KA 2401 IK")

    def login(self, email, password):
        self.open("/accounts/login/")
        self.fill("username", email)
        self.fill("password", password)
        self.submit()

    def test_active_rental_blocks_a_second_booking(self):
        booked_price = self.car.price
        self.login(self.client_user.email, "secret1")
        self.open(self.car.get_absolute_url())
        self.fill("days", "3")
        self.submit()
        self.assertIn("Оренду підтверджено", self.browser.page_source)

        self.car.price = 999
        self.car.save(update_fields=["price"])

        self.logout()
        self.login(self.other.email, "secret1")
        self.open(self.car.get_absolute_url())
        unavailable = self.browser.find_element(By.XPATH, "//button[contains(., 'Зараз недоступне')]")
        self.show(unavailable)
        time.sleep(1.2)
        self.assertFalse(unavailable.is_enabled())

        rental = Rental.objects.get(status=Rental.Status.ACTIVE)
        self.assertEqual(rental.days, 3)
        self.assertEqual(rental.car_plate, "KA 2401 IK")
        self.assertEqual(rental.total_price, booked_price * 3)
        self.assertEqual(rental.price_per_day, booked_price)
        self.assertEqual(Rental.objects.filter(status=Rental.Status.ACTIVE).count(), 1)
        time.sleep(2)
