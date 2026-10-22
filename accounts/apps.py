from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        from django.db.models.signals import post_migrate

        post_migrate.connect(_grant_role_permissions, dispatch_uid="accounts.grant_role_permissions")


def _grant_role_permissions(sender, **kwargs):
    from django.db.utils import OperationalError, ProgrammingError

    from accounts.groups import grant_group_permissions, sync_user_groups
    from accounts.models import User

    try:
        grant_group_permissions()
        for user in User.objects.filter(role__in=("admin", "manager")):
            sync_user_groups(user)
    except (OperationalError, ProgrammingError):
        return
