from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from authentication.models import VerificationCode

class AuthFlowTests(APITestCase):

    def setUp(self):
        # Create a user for testing
        self.user_email = "test@example.com"
        self.user_password = "password123"
        self.user = User.objects.create_user(
            username=self.user_email,
            email=self.user_email,
            password=self.user_password,
            is_active=True
        )

    def test_password_reset_flow(self):
        # Step 1: Request password reset (POST /password-reset/)
        response = self.client.post(
            "/api/auth/password-reset/", 
            {"email": self.user_email}, 
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Step 2: Create OTP manually (simulates email delivery)
        otp_code = "654321"
        VerificationCode.objects.create(
            email=self.user_email,
            code=otp_code,
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        # Step 3: Confirm password reset (POST /password-reset/confirm/)
        new_password = "newpassword123"
        response = self.client.post(
            "/api/auth/password-reset/confirm/", 
            {
                "email": self.user_email,
                "code": otp_code,
                "new_password": new_password
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "Password has been reset successfully.")

        # Step 4: Attempt login with new password
        response = self.client.post(
            "/api/auth/login/",
            {"email": self.user_email, "password": new_password},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "Login successful.")
