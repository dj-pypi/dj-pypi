from django.conf import settings
from django.core.files.storage import FileSystemStorage


class RepoStorageBackend(FileSystemStorage):
    base_location = settings.DATA_DIR
