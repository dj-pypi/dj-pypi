from django import forms
from django.core.exceptions import ValidationError

from legacy_upload.models import LegacyUpload, LegacyUploadFiletype
from legacy_upload.upload_handler import HashUploadedFile
from projects.models import Project


class LegacyUploadForm(forms.ModelForm):
    pyversion = forms.CharField(required=False)

    class Meta:
        model = LegacyUpload
        exclude = ("content_filename", "sha256_digest", "blake2b_digest")

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        assert isinstance(cleaned_data["content"], HashUploadedFile)

        # TODO: auto create projects (with permission)?
        try:
            project = Project.objects.get(name=cleaned_data["name"])
        except Project.DoesNotExist:
            raise ValidationError("Unknown project")
        else:
            if not self.request.user.has_perm("legacy_upload.add_legacyupload", project):
                raise ValidationError("Unknown project")

        # validate checksum
        actual_md5_digest = cleaned_data["content"].hash_digests["md5"]
        if cleaned_data["md5_digest"] != actual_md5_digest:
            raise ValidationError({"content": "MD5 digest does not match uploaded file."})

        # set `pyversion` to "source" if omitted and `filetype` is "sdist"
        if not self.cleaned_data.get("pyversion") and self.cleaned_data.get("filetype") == LegacyUploadFiletype.SDIST:
            self.cleaned_data["pyversion"] = "source"

        return cleaned_data

    def save(self, commit=True):
        self.instance.sha256_digest = self.cleaned_data["content"].hash_digests["sha256"]
        self.instance.blake2b_digest = self.cleaned_data["content"].hash_digests["blake2b"]
        return super().save(commit)
