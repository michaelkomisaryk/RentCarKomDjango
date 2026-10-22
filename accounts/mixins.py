from django.contrib.auth.mixins import UserPassesTestMixin

from accounts.groups import ADMIN_GROUP, STAFF_GROUPS


class RoleRequiredMixin(UserPassesTestMixin):
    allowed_groups = ()

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.groups.filter(name__in=self.allowed_groups).exists()


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_groups = (ADMIN_GROUP,)


class StaffRoleRequiredMixin(RoleRequiredMixin):
    allowed_groups = STAFF_GROUPS
