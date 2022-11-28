from django.contrib import admin

from legacy_upload.models import LegacyUpload


@admin.register(LegacyUpload)
class LegacyUploadAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "version",
        "filetype",
        "artefact",
    )
    list_filter = ("name", "filetype")
    readonly_fields = ("uploaded_at",)

    @admin.display(ordering="content_filename")
    def artefact(self, obj: LegacyUpload) -> str:
        return obj.content_filename
