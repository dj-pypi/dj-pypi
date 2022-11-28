from typing import Any, Sequence

from django.contrib import admin
from django.http import HttpRequest

from projects.admin import ProjectPermissionInline

from .models import AuthToken


class AuthTokenProjectPermissionInline(ProjectPermissionInline):
    exclude = ("user",)


@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ("__str__", "is_active")
    list_filter = ("created_by", "is_active")
    raw_id_fields = ("created_by",)
    fields = ("token", "description", "is_active", "created_at", "created_by")
    readonly_fields = ("created_by", "created_at")

    inlines = (AuthTokenProjectPermissionInline,)

    def save_model(self, request: HttpRequest, obj: AuthToken, form: Any, change: bool) -> None:
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request: HttpRequest, obj: AuthToken = None) -> Sequence[str]:
        if obj and obj.pk:
            return tuple(super().get_readonly_fields(request, obj)) + ("token",)
        return super().get_readonly_fields(request, obj)
