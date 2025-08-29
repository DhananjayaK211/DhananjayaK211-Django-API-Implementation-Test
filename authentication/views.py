import random
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .emails import send_otp_email
from .models import AuthToken, VerificationCode
from .serializers import (
    RegisterSerializer,
    VerifySerializer,
    LoginSerializer,
    UserSerializer,
)

User = get_user_model()


def _set_auth_cookie(response, token_key: str):
    max_age = getattr(settings, "AUTH_TOKEN_TTL_SECONDS", 604800)
    response.set_cookie(
        key=settings.AUTH_TOKEN_COOKIE_NAME,
        value=token_key,
        max_age=max_age,
        httponly=True,
        secure=not settings.DEBUG,   # ✅ only secure in production
        samesite="Lax",
    )


def _clear_auth_cookie(response):
    response.delete_cookie(settings.AUTH_TOKEN_COOKIE_NAME, samesite="Lax")


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    # Generate OTP
    code = f"{random.randint(0, 999999):06d}"
    VerificationCode.objects.create(
        email=user.email,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=10),
    )
    send_otp_email(user.email, code)

    return Response(
        {"message": "Registration successful. Please verify with OTP sent to email."},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register_verify(request):
    serializer = VerifySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data["email"].lower()
    code = serializer.validated_data["code"]

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        vc = VerificationCode.objects.filter(email=email, code=code).latest("created_at")
    except VerificationCode.DoesNotExist:
        return Response({"detail": "Invalid code."}, status=status.HTTP_400_BAD_REQUEST)

    if not vc.is_valid():
        return Response(
            {"detail": "Code expired or already used."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    vc.mark_used()
    user.is_active = True
    user.save(update_fields=["is_active"])
    return Response({"message": "Verification successful. You can now log in."})


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data["user"]

    token = AuthToken.objects.create(user=user)

    resp = Response({"message": "Login successful."})
    _set_auth_cookie(resp, token.key)
    return resp


@api_view(["GET"])
def me(request):
    data = UserSerializer(request.user).data
    return Response(data)


@api_view(["POST"])
def logout(request):
    token_key = request.COOKIES.get(settings.AUTH_TOKEN_COOKIE_NAME)
    if token_key:
        AuthToken.objects.filter(pk=token_key).delete()
    resp = Response({"message": "Logged out."})
    _clear_auth_cookie(resp)
    return resp


# ----------------- Password Reset -----------------

@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def password_reset_request(request):
    email = request.data.get("email")
    if not email:
        return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    code = f"{random.randint(0, 999999):06d}"
    VerificationCode.objects.create(
        email=email,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=10),
    )
    send_otp_email(email, code)

    return Response({"message": "Password reset OTP sent to your email."})


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def password_reset_confirm(request):
    email = request.data.get("email")
    code = request.data.get("code")
    new_password = request.data.get("new_password")

    if not all([email, code, new_password]):
        return Response({"detail": "Email, code and new_password are required."},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        vc = VerificationCode.objects.filter(email=email, code=code).latest("created_at")
    except VerificationCode.DoesNotExist:
        return Response({"detail": "Invalid code."}, status=status.HTTP_400_BAD_REQUEST)

    if not vc.is_valid():
        return Response({"detail": "Code expired or already used."}, status=status.HTTP_400_BAD_REQUEST)

    vc.mark_used()
    user.set_password(new_password)
    user.save()
    return Response({"message": "Password has been reset successfully."})
