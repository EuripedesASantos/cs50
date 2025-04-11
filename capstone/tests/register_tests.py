from django.test import Client
from django.urls import reverse

from tests.common_tests import CommonTests


class RegisterTests(CommonTests):
    def setUp(self):
        super().setUp()
        self.csrf_client = Client(enforce_csrf_checks=True)
        self.address = {
            'username': 'user20',
            'firstname': 'Michael',
            'lastname': 'Brown',
            'email': 'user20@mail.com',
            'password': 'user20',
            'confirmation': 'user20',
            'phone_number': '001-240-529-0471',
            "address": "7600 Camacho Corners",
            "city": "Beckyport",
            "complement": "Holtmouth, SC 07843",
            "gps_latitude": "12.456",
            "gps_longitude": "45.678"}

    def test_register_no_form(self):
        # Get CSRF token
        response = self.csrf_client.get(reverse('register'))
        csrftoken = response.cookies['csrftoken'].value

        response = self.csrf_client.post(reverse('register'), {},
                                         HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 400)

    def test_register_no_latitude(self):
        # Get CSRF token
        response = self.csrf_client.get(reverse('register'))
        csrftoken = response.cookies['csrftoken'].value

        address = self.address
        del address['gps_latitude']
        response = self.csrf_client.post(reverse('register'),
                                         address,
                                         HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 400)

    def test_register_no_longitude(self):
        # Get CSRF token
        response = self.csrf_client.get(reverse('register'))
        csrftoken = response.cookies['csrftoken'].value

        address = self.address
        del address['gps_longitude']
        response = self.csrf_client.post(reverse('register'),
                                         address,
                                         HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 400)

    def test_register_password_no_match(self):
        # Get CSRF token
        response = self.csrf_client.get(reverse('register'))
        csrftoken = response.cookies['csrftoken'].value

        address = self.address
        address['confirmation'] = '123456'
        response = self.csrf_client.post(reverse('register'),
                                         address, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 400)

    def test_register_user_exists(self):
        # Get CSRF token
        response = self.csrf_client.get(reverse('register'))
        csrftoken = response.cookies['csrftoken'].value

        address = self.address
        address['username'] = 'user1'
        response = self.csrf_client.post(reverse('register'),
                                         address, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 400)

    def test_register_no_address(self):
        # Get CSRF token
        response = self.csrf_client.get(reverse('register'))
        csrftoken = response.cookies['csrftoken'].value

        address = self.address
        del address['address']
        del address['city']
        del address['complement']
        response = self.csrf_client.post(reverse('register'),
                                         address, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 400)

    def test_register_no_city(self):
        # Get CSRF token
        response = self.csrf_client.get(reverse('register'))
        csrftoken = response.cookies['csrftoken'].value

        address = self.address
        del address['city']
        response = self.csrf_client.post(reverse('register'),
                                         address, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 400)

    def test_register_no_phone_number(self):
        # Get CSRF token
        response = self.csrf_client.get(reverse('register'))
        csrftoken = response.cookies['csrftoken'].value

        address = self.address
        del address['phone_number']
        response = self.csrf_client.post(reverse('register'),
                                         address,
                                         HTTP_X_CSRFTOKEN=csrftoken,
                                         follow=True)
        self.assertEqual(response.status_code, 400)

    def test_register_password_no_match(self):
        # Get CSRF token
        response = self.csrf_client.get(reverse('register'))
        csrftoken = response.cookies['csrftoken'].value
        self.address['confirmation'] ='no match'
        response = self.csrf_client.post(reverse('register'), self.address,
                                         HTTP_X_CSRFTOKEN=csrftoken,
                                         follow=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.get_message(response.content),'Passwords must match.')

    def test_register(self):
        # Get CSRF token
        response = self.csrf_client.get(reverse('register'))
        csrftoken = response.cookies['csrftoken'].value
        response = self.csrf_client.post(reverse('register'), self.address,
                                         HTTP_X_CSRFTOKEN=csrftoken,
                                         follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_message(response.content),'')
