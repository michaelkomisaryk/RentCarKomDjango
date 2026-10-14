from django.core.management import call_command
from django.test import TestCase

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
