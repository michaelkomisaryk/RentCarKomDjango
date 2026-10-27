import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By


class ChromeCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = webdriver.Chrome()
        cls.browser.set_window_rect(x=40, y=40, width=1280, height=780)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def prepare(self):
        return None

    def setUp(self):
        self.prepare()
        self.browser.get(self.live_server_url + "/")
        self.browser.find_element(By.CSS_SELECTOR, "button[value='uk']").click()
        time.sleep(0.8)

    def open(self, path):
        self.browser.get(self.live_server_url + path)
        time.sleep(0.8)

    def show(self, element):
        for _ in range(8):
            self.browser.execute_script(
                "const el = arguments[0];"
                "const root = document.scrollingElement;"
                "root.scrollTop = el.getBoundingClientRect().top + root.scrollTop - 180;",
                element,
            )
            time.sleep(0.25)
            top = self.browser.execute_script("return arguments[0].getBoundingClientRect().top;", element)
            if 80 < top < 460:
                return

    def fill(self, name, value):
        field = self.browser.find_element(By.NAME, name)
        self.show(field)
        self.browser.execute_script("arguments[0].focus(); arguments[0].value = '';", field)
        field.send_keys(value)
        time.sleep(0.45)

    def submit(self):
        button = self.browser.find_element(By.CSS_SELECTOR, "form.form-card button[type='submit']")
        self.show(button)
        button.click()
        time.sleep(1.2)

    def logout(self):
        self.browser.find_element(By.CSS_SELECTOR, "form[action*='logout'] button").click()
        time.sleep(0.8)
