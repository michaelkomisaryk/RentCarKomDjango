from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class Role(models.TextChoices):
    CLIENT = "client", "Client"
    MANAGER = "manager", "Manager"
    ADMIN = "admin", "Admin"


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email or not email.strip():
            raise ValueError("Email cannot be empty")
        email = self.normalize_email(email).strip().lower()
        name = extra_fields.get("name", "")
        if not str(name).strip():
            raise ValueError("Name cannot be empty")
        extra_fields["name"] = str(name).strip()
        extra_fields.setdefault("role", Role.CLIENT)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        from accounts.groups import sync_user_groups

        sync_user_groups(user)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("name", "Admin")
        extra_fields.setdefault("role", Role.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    rnokpp = models.CharField("RNOKPP", max_length=10, blank=True)
    driver_license = models.CharField(max_length=16, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        verbose_name = "користувач"
        verbose_name_plural = "користувачі"

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def is_admin_role(self):
        return self.role == Role.ADMIN

    @property
    def is_staff_role(self):
        return self.role in {Role.ADMIN, Role.MANAGER}

    @property
    def profile_is_complete(self):
        return bool(self.name and self.phone and self.rnokpp and self.driver_license)
