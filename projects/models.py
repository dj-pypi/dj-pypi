from django.conf import settings
from django.db import models
from django.urls import reverse

from projects.validators import ProjectNameValidator


class Project(models.Model):
    name = models.CharField(max_length=200, unique=True, validators=[ProjectNameValidator()])
    # TODO: normalized name?

    is_public = models.BooleanField()

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("simple-project-distribution-package-index", kwargs={"project_name": self.name})


class ProjectPermission(models.Model):
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    token = models.ForeignKey("token_auth.AuthToken", null=True, blank=True, on_delete=models.CASCADE)
    permissions = models.ManyToManyField(
        "auth.Permission",
        limit_choices_to=models.Q(
            codename__in=["add_project", "change_project", "delete_project", "view_project", "add_legacyupload"]
        ),
    )

    class Meta:
        constraints = (
            models.CheckConstraint(
                check=(models.Q(user__isnull=False) ^ models.Q(token__isnull=False)),
                name="%(app_label)s_%(class)s_user_or_token_required",
            ),
        )

    def __str__(self):
        return f"Project permissions for {self.project}"
