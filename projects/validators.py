import re

from django.core.validators import RegexValidator


class ProjectNameValidator(RegexValidator):
    # https://github.com/pypi/warehouse/blob/main/warehouse/forklift/legacy.py#L192
    regex = re.compile(r"^([A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])$", re.IGNORECASE)
