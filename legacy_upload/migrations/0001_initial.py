# Generated by Django 4.1.3 on 2022-11-28 20:41

from django.db import migrations, models

import legacy_upload.models
import legacy_upload.storage_backend
import projects.validators


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="LegacyUpload",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "content",
                    models.FileField(
                        storage=legacy_upload.storage_backend.RepoStorageBackend(),
                        upload_to=legacy_upload.models.upload_target,
                    ),
                ),
                ("md5_digest", models.CharField(max_length=32)),
                ("filetype", models.CharField(max_length=200)),
                ("pyversion", models.CharField(max_length=200)),
                ("metadata_version", models.CharField(max_length=200)),
                ("name", models.CharField(max_length=200, validators=[projects.validators.ProjectNameValidator()])),
                ("version", models.CharField(max_length=200)),
                ("content_filename", models.CharField(editable=False, max_length=200)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("sha256_digest", models.CharField(max_length=64)),
                ("blake2b_digest", models.CharField(max_length=128)),
            ],
        ),
        migrations.AddConstraint(
            model_name="legacyupload",
            constraint=models.UniqueConstraint(
                fields=("name", "version", "filetype", "pyversion"),
                name="'legacy_upload_legacyupload_unique_distribution_package",
            ),
        ),
    ]