from __future__ import annotations

import hashlib
from typing import Protocol

from django.core.files.uploadedfile import TemporaryUploadedFile
from django.core.files.uploadhandler import TemporaryFileUploadHandler


class Hash(Protocol):
    def update(self, data: bytes) -> None:
        ...

    def digest(self) -> bytes:
        ...

    def hexdigest(self) -> str:
        ...

    def copy(self) -> Hash:
        ...


class HashUploadedFile(TemporaryUploadedFile):
    HASH_ALGORITHMS = {
        "md5": hashlib.md5,
        "sha256": hashlib.sha256,
        "blake2b": hashlib.blake2b,
    }
    _hashes: dict[str, Hash]
    hash_digests: dict[str, str]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._hashes = {hash_algorithm: hash_obj() for hash_algorithm, hash_obj in self.HASH_ALGORITHMS.items()}
        self.hash_digests = {}

    def hash_data_chunk(self, raw_data):
        for hash_type, file_hash in self._hashes.items():
            file_hash.update(raw_data)

    def set_hash_digests(self):
        self.hash_digests = {
            hash_algorithm: file_hash.hexdigest() for hash_algorithm, file_hash in self._hashes.items()
        }


class HashUploadHandler(TemporaryFileUploadHandler):
    file: HashUploadedFile

    def new_file(self, *args, **kwargs):
        super(TemporaryFileUploadHandler, self).new_file(*args, **kwargs)
        self.file = HashUploadedFile(self.file_name, self.content_type, 0, self.charset, self.content_type_extra)

    def receive_data_chunk(self, raw_data, start):
        self.file.write(raw_data)
        self.file.hash_data_chunk(raw_data)

    def file_complete(self, file_size):
        self.file.set_hash_digests()
        return super().file_complete(file_size)
