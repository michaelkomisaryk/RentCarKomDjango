from django.contrib.auth.mixins import UserPassesTestMixin

class RoleRequiredMixin(UserPassesTestMixin):
    required_permission = ""

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.has_perm(self.required_permission)


class AdminRequiredMixin(RoleRequiredMixin):
    required_permission = "fleet.manage_fleet"


class StaffRoleRequiredMixin(RoleRequiredMixin):
    required_permission = "rentals.manage_rentals"
