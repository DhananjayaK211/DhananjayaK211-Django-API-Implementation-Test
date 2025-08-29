from django.conf import settings
from django.utils import timezone
from rest_framework import authentication, exceptions
from .models import AuthToken

class CookieTokenAuthentication(authentication.BaseAuthentication):
    """
    Authenticate using a token stored in an HTTP-only cookie.
    """
    cookie_name = getattr(settings, "AUTH_TOKEN_COOKIE_NAME", "auth_token")

    def authenticate(self, request):
        key = request.COOKIES.get(self.cookie_name)
        if not key:
            return None

        try:
            token = AuthToken.objects.select_related("user").get(pk=key)
        except AuthToken.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid auth token.")

        if token.expires_at <= timezone.now():
            raise exceptions.AuthenticationFailed("Auth token expired.")

        user = token.user
        if not user.is_active:
            raise exceptions.AuthenticationFailed("User inactive.")
        return (user, token)
