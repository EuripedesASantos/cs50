from django.urls import reverse

from tests.common_tests import CommonTests

from bs4 import BeautifulSoup


class LoginPageTests(CommonTests):
    fixtures = ['dumpdata_user.json']

    def __init__(self, method_name='runLoginPageTests'):
        super().__init__(method_name)
        self.page_name = 'index'
        self.page_title_logout = 'Login'
        self.page_title_login = 'Courier System'

    @staticmethod
    def get_title(html: str) -> str:
        return BeautifulSoup(html, 'html.parser').title.string

    # Try accessing the Courier page without being logged in
    def test_access_page_logout(self):
        response = self.csrf_client.get(reverse(self.page_name), follow=True)
        # 302: Redirect
        self.assertEqual(self.get_title(response.content), self.page_title_logout)

    def loggin_user(self):
        self.csrf_client.login(username="user1", password="user1")

    # Try accessing the Courier page being logged in
    def test_access_page_login(self):
        self.loggin_user()
        response = self.csrf_client.get(reverse(self.page_name), follow=True)
        self.assertEqual(self.get_title(response.content), self.page_title_login)
