from typing import Any

from django.contrib import admin
from django.http import HttpRequest

from token_auth.models import AuthToken

from .models import Project, ProjectPermission


class ProjectPermissionInline(admin.TabularInline):
    model = ProjectPermission
    raw_id_fields = ("project",)
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "is_public")
    list_filter = ("is_public", "created_by")
    raw_id_fields = ("created_by",)
    readonly_fields = ("created_by", "created_at", "updated_at")
    search_fields = ("name",)

    inlines = (ProjectPermissionInline,)

    def save_model(self, request: HttpRequest, obj: AuthToken, form: Any, change: bool) -> None:
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
