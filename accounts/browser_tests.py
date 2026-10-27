import time

from selenium.webdriver.common.by import By

from accounts.chrome import ChromeCase
from accounts.models import Role, User


class RegistrationChromeTests(ChromeCase):
    def test_registration_creates_a_client(self):
        self.open("/accounts/register/")
        self.fill("name", "New Client")
        self.fill("email", "New@Example.com")
        self.fill("phone", "0671234567")
        self.fill("rnokpp", "1234567890")
        self.fill("driver_license", "кіа654321")
        self.fill("password1", "secret1")
        self.fill("password2", "secret1")
        self.submit()
        self.assertIn("Зареєстровано. Увійдіть.", self.browser.page_source)

        self.fill("username", "new@example.com")
        self.fill("password", "secret1")
        self.submit()
        self.assertIn("КЛІЄНТ", self.browser.page_source)
        self.assertNotIn("Усі оренди", self.browser.page_source)
        self.assertNotIn("Додати авто", self.browser.page_source)

        user = User.objects.get(email="new@example.com")
        self.assertEqual(user.role, Role.CLIENT)
        self.assertEqual(user.name, "New Client")
        self.assertEqual(user.phone, "+380671234567")
        self.assertEqual(user.rnokpp, "1234567890")
        self.assertEqual(user.driver_license, "КІА 654321")
        time.sleep(2)
