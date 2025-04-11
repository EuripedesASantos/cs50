from bs4 import BeautifulSoup
from django.urls import reverse

from tests.common_tests import CommonTests


class ShipmentsTests(CommonTests):
    fixtures = ['dumpdata.json']

    def __init__(self, method_name='runShipmentsTests'):
        super().__init__(method_name)
        self.shipment = {
            'user_receiver_id': 2,
            'contents': 'Used Salad',
            'address_sender_id': 1,
            'address_deliver_id': 2
        }

    def setUp(self):
        super().setUp()
        # User to receive must be a courier
        self.login()

    def login(self, username='user1'):
        return self.csrf_client.login(username=username, password=username)

    def get_csrftoken(self, page_name):
        # Get CSRF token
        response = self.csrf_client.get(reverse(page_name))
        return response.cookies['csrftoken'].value

    def get_message(self, html: str) -> str:
        message, _, _ = self.get_message_title_error(html)
        return message

    def get_title(self, html: str) -> str:
        _, title, _ = self.get_message_title_error(html)
        return title

    def get_errorlist(self, html: str) -> str:
        _, _, errorlist = self.get_message_title_error(html)
        return errorlist

    @staticmethod
    def get_message_title_error(html: str) -> tuple:
        result = BeautifulSoup(html, 'html.parser')
        message = result.find(id='message')
        errorlist_ul = result.find('ul', {"class": "errorlist"})
        if result.title:
            title = result.title.string
        else:
            title = ''
        if message:
            message = message.string
        else:
            message = ''
        errorlist = ''
        if errorlist_ul:
            for li in errorlist_ul('li'):
                errorlist += li.get_text().split('\n')[0] + '\n'

        return message, title, errorlist

    def test_shipments_new(self):
        response = self.csrf_client.post(
            reverse('new-shipment'),
            self.shipment,
            HTTP_X_CSRFTOKEN=self.get_csrftoken('new-shipment'),
            follow=True)

        message, title, errorlist = self.get_message_title_error(response.content)

        self.assertEqual(errorlist, '')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message, '')
        self.assertEqual(title, 'Courier System')

    def test_shipments_new_get(self):
        response = self.csrf_client.get(reverse('new-shipment'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_message(response.content), '')

    def test_shipments_new_empty(self):
        response = self.csrf_client.post(
            reverse('new-shipment'),
            data={},
            HTTP_X_CSRFTOKEN=self.get_csrftoken('new-shipment'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_message(response.content),
                         'Form is invalid!')

    def test_shipments_cancel(self):
        response = self.csrf_client.post(
            reverse('cancel-shipment'),
            data={"shipment_id": 1},
            HTTP_X_CSRFTOKEN=self.get_csrftoken('index'),
            follow=True)

        message, title, errorlist = self.get_message_title_error(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message, '')
        self.assertEqual(title, 'Courier System')
        self.assertEqual(errorlist, '')

    def test_shipments_cancel_id_error(self):
        response = self.csrf_client.post(
            reverse('cancel-shipment'),
            data={"shipment_id": 99},
            HTTP_X_CSRFTOKEN=self.get_csrftoken('index'),
            follow=True)

        message, title, errorlist = self.get_message_title_error(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message, 'Error canceling shipment: Shipment matching query does not exist.!')
        self.assertEqual(title, 'Courier System')
        self.assertEqual(errorlist, '')

    def test_shipments_cancel_id_empty(self):
        response = self.csrf_client.post(
            reverse('cancel-shipment'),
            data={},
            HTTP_X_CSRFTOKEN=self.get_csrftoken('index'),
            follow=True)

        message, title, errorlist = self.get_message_title_error(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message, 'Unable to cancel shipment!')
        self.assertEqual(title, 'Courier System')
        self.assertEqual(errorlist, '')

    def test_shipments_cancel_get(self):
        response = self.csrf_client.get(
            reverse('cancel-shipment'))

        message, title, errorlist = self.get_message_title_error(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message, 'Use POST form to cancel shipment!')
        self.assertEqual(title, 'Courier System')
        self.assertEqual(errorlist, '')

    def test_shipments_receipt(self):
        response = self.csrf_client.get(reverse('receipt-shipment'),
                                         follow=True)

        message, title, errorlist = self.get_message_title_error(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message, '')
        self.assertEqual(title, 'Shipment to Receipt')
        self.assertEqual(errorlist, '')

    def test_shipments_deliver(self):
        response = self.csrf_client.get(reverse('deliver-shipment'),
                                         follow=True)

        message, title, errorlist = self.get_message_title_error(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message, '')
        self.assertEqual(title, 'Shipment to Deliver')
        self.assertEqual(errorlist, '')
