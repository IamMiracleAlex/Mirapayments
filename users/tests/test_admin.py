from django.test import TestCase
from django.urls import reverse
# from django.http import HttpRequest

from users.tests.factories import UserFactory
from users.models import User


class UserAdminTest(TestCase):

    def setUp(self):
        self.user = UserFactory(is_staff=True, is_superuser=True)
        self.client.force_login(self.user) 

    def test_changelist_view(self):
        '''Assert user change list view loads well'''

        url = reverse("admin:%s_%s_changelist" % (self.user._meta.app_label, self.user._meta.model_name))
        page = self.client.get(url)
        self.assertEqual(page.status_code, 200)

    def test_change_view(self):
        '''Assert user change view page opens successfully'''

        url = reverse("admin:%s_%s_change" % (self.user._meta.app_label, self.user._meta.model_name), args=(self.user.pk,))
        page = self.client.get(url)
        self.assertEqual(page.status_code, 200)


    def test_export_as_csv(self):
        '''assert that export_to_csv() works'''

        queryset = UserFactory.create_batch(size=10)
        # request = HttpRequest()

        result = self.user_admin.export_as_csv(self.request, queryset)
        #csv is created and returns success status code
        self.assertEqual(result.status_code, 200) 
