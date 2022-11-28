from django.contrib.auth.backends import BaseBackend
from django.http import HttpRequest

from token_auth.models import AuthToken


class TokenAuthBackend(BaseBackend):
    def authenticate(self, request: HttpRequest, token: str = None, **kwargs) -> AuthToken | None:
        try:
            return AuthToken.objects.get(token=token, is_active=True)
        except AuthToken.DoesNotExist:
            return
