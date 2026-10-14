from django.contrib.auth.mixins import UserPassesTestMixin

from accounts.models import Role


class RoleRequiredMixin(UserPassesTestMixin):
    allowed_roles = ()

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.role in self.allowed_roles


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = (Role.ADMIN,)


class StaffRoleRequiredMixin(RoleRequiredMixin):
    allowed_roles = (Role.ADMIN, Role.MANAGER)
