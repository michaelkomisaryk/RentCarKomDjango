from django.contrib.auth.models import Group

ADMIN_GROUP = "admin"
MANAGER_GROUP = "manager"
STAFF_GROUPS = (ADMIN_GROUP, MANAGER_GROUP)


def sync_user_groups(user):
    """Keep Django groups aligned with the account role."""
    named = {name: Group.objects.get_or_create(name=name)[0] for name in STAFF_GROUPS}
    user.groups.remove(*named.values())
    if user.role == "admin":
        user.groups.add(named[ADMIN_GROUP])
    elif user.role == "manager":
        user.groups.add(named[MANAGER_GROUP])
