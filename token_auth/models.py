from django.conf import settings
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.itercompat import is_iterable


def generate_token():
    return get_random_string(64)


class AuthToken(models.Model):
    token = models.CharField(max_length=128, default=generate_token)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.description or f"AuthToken {self.pk}"

    # implement parts of the AbstractUser/PermissionsMixin interface
    # TODO: use PermissionsMixin and limit permissions?

    is_superuser = False
    is_staff = False

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    def get_user_permissions(self, obj=None):
        return set()

    def get_group_permissions(self, obj=None):
        return set()

    def get_all_permissions(self, obj=None):
        return set()

    def has_perm(self, perm, obj=None) -> bool:
        from projects.models import Project

        # check object permissions for projects
        if isinstance(obj, Project):
            app_label, codename = perm.split(".")
            return obj.projectpermission_set.filter(
                token=self, permissions__content_type__app_label=app_label, permissions__codename=codename
            ).exists()

        return False

    def has_perms(self, perm_list, obj=None):
        """
        Return True if the user has each of the specified permissions. If
        object is passed, check if the user has all required perms for it.
        """
        if not is_iterable(perm_list) or isinstance(perm_list, str):
            raise ValueError("perm_list must be an iterable of permissions.")
        return all(self.has_perm(perm, obj) for perm in perm_list)
