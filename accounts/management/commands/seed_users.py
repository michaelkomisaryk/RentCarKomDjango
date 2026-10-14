from django.core.management.base import BaseCommand

from accounts.models import Role, User


DEFAULT_USERS = (
    {
        "name": "Admin",
        "email": "admin@rentcarkom.com",
        "password": "admin123",
        "role": Role.ADMIN,
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "name": "Manager",
        "email": "manager@rentcarkom.com",
        "password": "manager123",
        "role": Role.MANAGER,
        "is_staff": True,
        "is_superuser": False,
    },
)


class Command(BaseCommand):
    help = "Create the default admin and manager accounts."

    def handle(self, *args, **options):
        for data in DEFAULT_USERS:
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "name": data["name"],
                    "role": data["role"],
                    "is_staff": data["is_staff"],
                    "is_superuser": data["is_superuser"],
                },
            )
            if created:
                user.set_password(data["password"])
                user.save(update_fields=["password"])
                self.stdout.write(self.style.SUCCESS(f"Created {user.email}"))
            else:
                self.stdout.write(f"Already exists: {user.email}")
