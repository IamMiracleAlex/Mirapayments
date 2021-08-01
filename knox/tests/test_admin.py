from django.test import TestCase
from django.urls import reverse

from users.tests.factories import UserFactory
from knox.tests.factories import AuthTokenFactory


class UserAdminTest(TestCase):

    def setUp(self):
        self.user = UserFactory(is_staff=True, is_superuser=True)
        self.token = AuthTokenFactory(user=self.user)
        self.client.force_login(self.user)

    def test_changelist_view(self):
        '''Assert knox change list view loads well'''

        url = reverse("admin:%s_%s_changelist" % (self.token._meta.app_label, self.token._meta.model_name))
        page = self.client.get(url)
        self.assertEqual(page.status_code, 200)

    def test_change_view(self):
        '''Assert knox change view page opens successfully'''

        url = reverse("admin:%s_%s_change" % (self.token._meta.app_label, self.token._meta.model_name), args=(self.token.pk,))
        page = self.client.get(url)
        self.assertEqual(page.status_code, 200)
