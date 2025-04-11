from bs4 import BeautifulSoup
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse


class CommonTests(TestCase):
    fixtures = ['dumpdata.json']

    def __init__(self, method_name='runTest'):
        super().__init__(method_name)
        self.csrf_client = None

    def setUp(self):
        if not self.csrf_client:
            self.csrf_client = Client(enforce_csrf_checks=True)

    def get_csrftoken(self, page_name: str):
        # Get CSRF token
        response = self.csrf_client.get(reverse(page_name))
        return response.cookies['csrftoken'].value

    @staticmethod
    def get_message(html: str) -> str:
        result = BeautifulSoup(html, 'html.parser').find(id='message')
        if result:
            return result.string
        else:
            return ''


class LoginCommonTests(CommonTests):
    def setUp(self):
        super().setUp()
        self.csrf_client.logout()
        self.create_user()

    @staticmethod
    def create_user():
        User.objects.create_user(username="user1", email="user1@mail.com", password="user1")

    def login(self):
        return self.csrf_client.login(username="user1", password="user1")

    def test_correct_login(self):
        self.assertTrue(self.login())

    def test_login_wrong_password(self):
        self.assertFalse(self.csrf_client.login(username="user1", password="password wrong"))


class PostCommonTests(CommonTests):
    fixtures = ['dumpdata_user.json']

    def setUp(self):
        super().setUp()
        self.csrf_client.login(username="user1", password="user1")
