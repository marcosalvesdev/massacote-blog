from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


class PasswordResetFlowTests(TestCase):
    """End-to-end walk through requesting and completing a password reset.

    The confirm/complete steps build the reset URL directly from the token
    generator instead of parsing it out of the sent email body, since the
    raw email is quoted-printable-wrapped and not meant to be scraped.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="marcos", password="old-password-123", email="marcos@example.com"
        )

    def test_requesting_a_reset_sends_one_email(self):
        response = self.client.post(
            reverse("password_reset"), {"email": "marcos@example.com"}
        )

        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("marcos@example.com", mail.outbox[0].to)

    def test_requesting_a_reset_for_unknown_email_sends_no_email(self):
        self.client.post(reverse("password_reset"), {"email": "nobody@example.com"})

        self.assertEqual(len(mail.outbox), 0)

    def test_full_reset_flow_lets_user_log_in_with_new_password(self):
        self.client.post(reverse("password_reset"), {"email": "marcos@example.com"})

        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        confirm_get_url = reverse(
            "password_reset_confirm", kwargs={"uidb64": uid, "token": token}
        )
        confirm_get_response = self.client.get(confirm_get_url, follow=True)
        set_password_url = confirm_get_response.redirect_chain[-1][0]

        confirm_post_response = self.client.post(
            set_password_url,
            {"new_password1": "a-brand-new-pw-456", "new_password2": "a-brand-new-pw-456"},
        )
        self.assertRedirects(confirm_post_response, reverse("password_reset_complete"))

        self.assertFalse(
            self.client.login(username="marcos", password="old-password-123")
        )
        self.assertTrue(
            self.client.login(username="marcos", password="a-brand-new-pw-456")
        )
