from django.db import migrations


def assign_groups(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    Group = apps.get_model("auth", "Group")
    admin_group, _created = Group.objects.get_or_create(name="admin")
    manager_group, _created = Group.objects.get_or_create(name="manager")
    for user in User.objects.all():
        user.groups.remove(admin_group, manager_group)
        if user.role == "admin":
            user.groups.add(admin_group)
        elif user.role == "manager":
            user.groups.add(manager_group)


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_user_driver_license_user_phone_user_rnokpp"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(assign_groups, migrations.RunPython.noop),
    ]
