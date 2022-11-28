import base64

from django.contrib import auth
from django.core.exceptions import BadRequest, PermissionDenied
from django.utils.deprecation import MiddlewareMixin

from token_auth.models import AuthToken


class TokenAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request) -> None:
        if not request.headers.get("Authorization"):
            return

        try:
            method, encoded_credentials = request.headers["Authorization"].split(" ")
            decoded_credentials = base64.b64decode(encoded_credentials).decode()

            if method.lower() != "basic":
                return

            if ":" in decoded_credentials:
                user, token = decoded_credentials.split(":")
            else:
                user = ""
                token = decoded_credentials
        except ValueError:
            raise BadRequest("Malformed Authorization header")

        if user and user != "__token__":
            if django_user := auth.authenticate(request, username=user, password=token):
                request.user = django_user
                return

        # token as username (https://<token>@url)
        if user and not token:
            token = user

        if not AuthToken.objects.filter(token=token, is_active=True).exists():
            raise PermissionDenied("Unknown user or token")

        if token_user := auth.authenticate(request, token=token):
            request.user = token_user
