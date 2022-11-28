from __future__ import annotations

from django.db import models
from django.db.models import UniqueConstraint
from django.urls import reverse

from legacy_upload.storage_backend import RepoStorageBackend
from projects.validators import ProjectNameValidator


def upload_target(instance: LegacyUpload, filename):
    instance.content_filename = filename
    return f"projects/{instance.name}/{instance.version}/{filename}"


class LegacyUploadFiletype(models.TextChoices):
    BDIST_WHEEL = "bdist_wheel"
    SDIST = "sdist"


class LegacyUpload(models.Model):
    # :action = 'file_upload'
    # protocol_version = 1
    content = models.FileField(storage=RepoStorageBackend(), upload_to=upload_target)
    md5_digest = models.CharField(max_length=32)
    filetype = models.CharField(max_length=200)  # TODO
    pyversion = models.CharField(max_length=200)  # TODO
    metadata_version = models.CharField(max_length=200)  # TODO
    name = models.CharField(max_length=200, validators=[ProjectNameValidator()])  # TODO
    version = models.CharField(max_length=200)  # TODO

    # not part of the upload form
    content_filename = models.CharField(max_length=200, editable=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    sha256_digest = models.CharField(max_length=64)
    blake2b_digest = models.CharField(max_length=128)
    # yanked = models.BooleanField(default=False, editable=False)  # TODO

    class Meta:
        constraints = (
            UniqueConstraint(
                fields=("name", "version", "filetype", "pyversion"),
                name="'%(app_label)s_%(class)s_unique_distribution_package",
            ),
        )

    def clean(self):
        if self.filetype == LegacyUploadFiletype.SDIST and not self.pyversion:
            self.pyversion = "source"

    def get_absolute_url(self):
        return reverse(
            "download-distribution-package", kwargs={"project_name": self.name, "path": self.content_filename}
        )
