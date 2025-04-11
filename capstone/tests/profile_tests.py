import json

from django.urls import reverse

from courier.models import PhoneNumber, Address
from tests.login_tests import LoginPageTests
from tests.common_tests import PostCommonTests

from bs4 import BeautifulSoup


class ProfilePageTests(LoginPageTests):
    def __init__(self, method_name='runProfilePageTests'):
        super().__init__(method_name)
        self.page_name = 'profile'
        self.page_title_logout = 'Login'
        self.page_title_login = 'User Profile'

    def test_profile_access_page_logout(self):
        super().test_access_page_logout()

    def test_profile_access_page_login(self):
        super().test_access_page_login()


class ProfilePostsTests(PostCommonTests):
    def setUp(self):
        super().setUp()

        self.address = {
            "address": "7600 Camacho Corners",
            "city": "Beckyport",
            "complement": "Holtmouth, SC 07843",
            "gps_latitude": "12.456",
            "gps_longitude": "45.678"}

    @staticmethod
    def get_message(html: str) -> str:
        result = BeautifulSoup(html, 'html.parser').find(id='message')
        if result:
            return result.string
        else:
            return ''

    def post_address_add(self, form):
        response = self.csrf_client.post(reverse('add-address'), form,
                                         HTTP_X_CSRFTOKEN=self.get_csrftoken('profile'))

        return response.context[0]['message']

    def test_address_add(self):
        msg = self.post_address_add(form=self.address)
        self.assertIsNone(msg)
        self.assertTrue(Address.objects.filter(address=self.address['address']).exists())

    def test_address_add_empty(self):
        self.assertEqual(self.post_address_add(form={}), 'Form information invalid!')

    def test_address_add_no_latitude(self):
        del self.address['gps_latitude']
        self.assertEqual(self.post_address_add(form=self.address), 'Invalid latitude information!')

    def test_address_add_no_longitude(self):
        del self.address['gps_longitude']
        self.assertEqual(self.post_address_add(form=self.address), 'Invalid longitude information!')

    def test_address_add_no_city(self):
        del self.address['city']
        self.assertEqual(self.post_address_add(form=self.address), 'Form information invalid!')

    def test_address_add_no_address(self):
        del self.address['address']
        self.assertEqual(self.post_address_add(form=self.address), 'Form information invalid!')

    def test_address_add_no_complement(self):
        del self.address['complement']
        msg = self.post_address_add(form=self.address)
        self.assertIsNone(msg)
        self.assertTrue(Address.objects.filter(address=self.address['address']).exists())

    def test_address_update(self):
        # Create a new address
        self.test_address_add()
        # Remove the created address
        address = self.address
        address['id'] = '1'
        address['address'] = address['address'] + ' updated'
        response = self.csrf_client.post(reverse('update-address'),
                                         address,
                                         HTTP_X_CSRFTOKEN=self.get_csrftoken('profile'),
                                         follow=True)
        # Operation successful but returns no content
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Address.objects.filter(address=self.address['address']).exists())

    def test_address_update_id_empty(self):
        # Create a new address
        self.test_address_add()
        # Remove the created address
        address = self.address
        address['id'] = ''
        response = self.csrf_client.post(reverse('update-address'),
                                         address,
                                         HTTP_X_CSRFTOKEN=self.get_csrftoken('profile'),
                                         follow=True)
        # Operation successful but returns no content
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content)['error'],
                         'PUT request without id of address to be updated!')

    def test_address_update_no_id(self):
        # Create a new address
        self.test_address_add()
        # Remove the created address
        response = self.csrf_client.post(reverse('update-address'),
                                         self.address,
                                         HTTP_X_CSRFTOKEN=self.get_csrftoken('profile'),
                                         follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content)['error'],
                         'PUT request without id of address to be updated!')

    def test_address_update_id_error(self):
        address = self.address
        address['id'] = 99
        response = self.csrf_client.post(reverse('update-address'),
                                         address,
                                         HTTP_X_CSRFTOKEN=self.get_csrftoken('profile'),
                                         follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[0]['message'],
                         'Error update address: Address matching query does not exist.')

    def test_address_update_get(self):
        response = self.csrf_client.get(reverse('update-address'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[0]['title'], 'User Profile')

    def test_address_remove(self):
        # Create a new address
        self.test_address_add()
        # Remove the created address
        response = self.csrf_client.put(reverse('remove-address'),
                                        content_type="application/json",
                                        data={"id": "1"},
                                        HTTP_X_CSRFTOKEN=self.get_csrftoken('profile'))
        # Operation successful but returns no content
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Address.objects.filter(id=1).exists())

    def test_address_remove_id_empty(self):
        # Create a new address
        self.test_address_add()
        # Remove the created address
        response = self.csrf_client.put(reverse('remove-address'),
                                        content_type="application/json",
                                        data={"id": ""},
                                        HTTP_X_CSRFTOKEN=self.get_csrftoken('profile'))
        # Operation successful but returns no content
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content)['error'], 'PUT request without id of address to be removed!')

    def test_address_remove_id_error(self):
        # Create a new address
        self.test_address_add()
        # Remove the created address
        response = self.csrf_client.put(reverse('remove-address'),
                                        content_type="application/json",
                                        data={"id": "2"},
                                        HTTP_X_CSRFTOKEN=self.get_csrftoken('profile'))
        # Operation successful but returns no content
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content)['error'],
                         'Error removing address: (Address matching query does not exist.).')

    def test_address_remove_get(self):
        # Create a new address
        self.test_address_add()
        # Remove the created address
        response = self.csrf_client.get(reverse('remove-address'),
                                        content_type="application/json",
                                        data={"id": "2"},
                                        HTTP_X_CSRFTOKEN=self.get_csrftoken('profile'))
        # Operation successful but returns no content
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content)['error'], 'Try remove address without PUT request!')

    def test_phone_add(self):
        response = self.csrf_client.post(reverse('add-phone'), {'phone_number': '328-296-7720'},
                                         HTTP_X_CSRFTOKEN=self.get_csrftoken('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(PhoneNumber.objects.filter(phone_number='328-296-7720').exists())

    def test_phone_add_empty(self):
        response = self.csrf_client.post(reverse('add-phone'), {},
                                         HTTP_X_CSRFTOKEN=self.get_csrftoken('profile'))
        self.assertEqual(self.get_message(response.content),
                         'Error: Invalide information provided insert new phone number!')

    def test_phone_add_get(self):
        response = self.csrf_client.get(reverse('add-phone'), {'phone_number': '328-296-7720'},
                                        HTTP_X_CSRFTOKEN=self.get_csrftoken('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_message(response.content), '')

    def phone_update_put(self, data=None):
        # Create a new phone
        self.test_phone_add()
        # update created phone
        if data:
            response = self.csrf_client.put(reverse('update-phone'),
                                            content_type="application/json",
                                            data=data,
                                            HTTP_X_CSRFTOKEN=self.get_csrftoken('profile'))
        else:
            response = self.csrf_client.put(reverse('update-phone'),
                                            HTTP_X_CSRFTOKEN=self.get_csrftoken('profile'))

        try:
            error = json.loads(response.content)['error']
        except:
            error = ''

        return response.status_code, error

    def test_phone_update(self):
        status_code, error = self.phone_update_put(data={"id": "1", "phone_number": "328-296-7720"})
        # Operation successful but returns no content
        self.assertEqual(status_code, 204)
        self.assertEqual(error, '')

    def test_phone_update_empty(self):
        status_code, error = self.phone_update_put()
        # Operation successful but returns no content
        self.assertEqual(status_code, 404)
        self.assertEqual(error, 'PUT request without with empty form!')

    def test_phone_update_no_phone(self):
        status_code, error = self.phone_update_put(data={"id": "1"})
        # Operation successful but returns no content
        self.assertEqual(status_code, 404)
        self.assertEqual(error, 'PUT request without new value of phone number to be updated!')
