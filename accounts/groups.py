from django.contrib.auth.models import Group, Permission

ADMIN_GROUP = "admin"
MANAGER_GROUP = "manager"
STAFF_GROUPS = (ADMIN_GROUP, MANAGER_GROUP)


def grant_group_permissions():
    """Give the admin and manager groups their custom permissions."""
    try:
        manage_fleet = Permission.objects.get(content_type__app_label="fleet", codename="manage_fleet")
        manage_rentals = Permission.objects.get(
            content_type__app_label="rentals",
            codename="manage_rentals",
        )
    except Permission.DoesNotExist:
        return
    admin_group, _created = Group.objects.get_or_create(name=ADMIN_GROUP)
    manager_group, _created = Group.objects.get_or_create(name=MANAGER_GROUP)
    admin_group.permissions.add(manage_fleet, manage_rentals)
    manager_group.permissions.add(manage_rentals)


def sync_user_groups(user):
    """Keep Django groups aligned with the account role."""
    grant_group_permissions()
    named = {name: Group.objects.get_or_create(name=name)[0] for name in STAFF_GROUPS}
    user.groups.remove(*named.values())
    if user.role == "admin":
        user.groups.add(named[ADMIN_GROUP])
    elif user.role == "manager":
        user.groups.add(named[MANAGER_GROUP])
