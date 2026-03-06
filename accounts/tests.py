from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import FaceCredential


class AccountAuthFlowTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()

    def test_captcha_endpoint_returns_png_and_sets_session(self):
        response = self.client.get(reverse("accounts:captcha_image"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")
        self.assertIn("login_captcha", self.client.session)
        self.assertEqual(len(self.client.session["login_captcha"]), 5)

    def test_login_fails_with_wrong_captcha(self):
        self.user_model.objects.create_user(
            email="shopper@example.com",
            password="StrongPass123!",
        )
        self.client.get(reverse("accounts:captcha_image"))

        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "shopper@example.com",
                "password": "StrongPass123!",
                "captcha": "WRONG",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid captcha. Please try again.")

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="test@example.com",
    )
    def test_password_reset_redirects_to_done_page(self):
        response = self.client.post(
            reverse("accounts:password_forgot"),
            {"email": "nobody@example.com"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:password_reset_done"))

    def test_face_enrollment_requires_login(self):
        response = self.client.post(
            reverse("accounts:face_enroll"),
            data='{"descriptor":[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,3.0,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,4.0,4.1,4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,5.0,5.1,5.2,5.3,5.4,5.5,5.6,5.7,5.8,5.9,6.0,6.1,6.2,6.3,6.4]}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 302)

    def test_face_login_success_after_enrollment(self):
        user = self.user_model.objects.create_user(
            email="faceuser@example.com",
            password="StrongPass123!",
        )
        descriptor = [float(index) / 10.0 for index in range(128)]
        FaceCredential.objects.create(user=user, descriptor=descriptor)

        response = self.client.post(
            reverse("accounts:face_login"),
            data={
                "email": "faceuser@example.com",
                "descriptor": descriptor,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"ok": True, "redirect_url": reverse("products:home")},
        )

    def test_face_login_is_case_insensitive_on_email(self):
        user = self.user_model.objects.create_user(
            email="FaceUserCaps@example.com",
            password="StrongPass123!",
        )
        descriptor = [float(index) / 10.0 for index in range(128)]
        FaceCredential.objects.create(user=user, descriptor=descriptor)

        response = self.client.post(
            reverse("accounts:face_login"),
            data={
                "email": "faceusercaps@example.com",
                "descriptor": descriptor,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

    def test_face_login_without_email_matches_enrolled_face(self):
        user = self.user_model.objects.create_user(
            email="faceonly@example.com",
            password="StrongPass123!",
        )
        descriptor = [float(index) / 10.0 for index in range(128)]
        FaceCredential.objects.create(user=user, descriptor=descriptor)

        response = self.client.post(
            reverse("accounts:face_login"),
            data={
                "descriptor": descriptor,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
