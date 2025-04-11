from django.urls import reverse

from tests.common_tests import CommonTests


class CourierAccessTests(CommonTests):
    def setUp(self):
        super().setUp()

    def test_courier_access_index(self):
        response = self.csrf_client.get('')
        # 302: Redirect
        self.assertEqual(response.status_code, 302)

    def test_courier_access_index_redirect(self):
        # Same test with redirect
        response = self.csrf_client.get(reverse('index'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_courier_access_index(self):
        response = self.csrf_client.get(reverse('index'))
        # 302: Redirect
        self.assertEqual(response.status_code, 302)

    def test_courier_access_login_get(self):
        response = self.csrf_client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_courier_access_login_wrong(self):
        response = self.csrf_client.post(reverse('login'),
                                         {"username": "john", "password": "smith"},
                                         HTTP_X_CSRFTOKEN=self.get_csrftoken('login'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_message(response.content), 'Invalid username and/or password.')

    def test_courier_access_login_no_csrf(self):
        response = self.csrf_client.post(reverse('login'), {"username": "user1", "password": "user1"})
        # 403: Forbidden: CSRF verification failed. Request aborted.
        self.assertEqual(response.status_code, 403)

    def test_courier_access_login(self):
        response = self.csrf_client.post(reverse('login'),
                                         {"username": "user1", "password": "user1"},
                                         HTTP_X_CSRFTOKEN=self.get_csrftoken('login'),
                                         follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_message(response.content), '')

class CourierOpeationTests(CommonTests):
    def setUp(self):
        super().setUp()
        self.csrf_client.login(username="user1", password="user1")

    def test_courier_receipt(self):
        response = self.csrf_client.post(reverse('courier-receive'),
                                         {'shipment_id': 16, 'check_code_get': '3915'},
                                         HTTP_X_CSRFTOKEN=self.get_csrftoken('courier-receive'),
                                         follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_message(response.content), '')

    def test_courier_receipt_wrong_code(self):
        response = self.csrf_client.post(reverse('courier-receive'),
                                         {'shipment_id': 16, 'check_code_get': '9999'},
                                         HTTP_X_CSRFTOKEN=self.get_csrftoken('courier-receive'),
                                         follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_message(response.content), 'Error receiving shipment: Check code incorrect!')

    def test_courier_receipt_ordered(self):
        response = self.csrf_client.post(reverse('courier-receive'),
                                         {'shipment_id': 13, 'check_code_get': '1396'},
                                         HTTP_X_CSRFTOKEN=self.get_csrftoken('courier-receive'),
                                         follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_message(response.content), 'Error receiving shipment: Data inconsistence detected!')

    def test_courier_receipt_no_checkcode(self):
        response = self.csrf_client.post(reverse('courier-receive'),
                                         {'shipment_id': 13},
                                         HTTP_X_CSRFTOKEN=self.get_csrftoken('courier-receive'),
                                         follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_message(response.content), 'Form is invalid!')

    def test_courier_receipt_no_id(self):
        response = self.csrf_client.post(reverse('courier-receive'),
                                         {'check_code_get': '1396'},
                                         HTTP_X_CSRFTOKEN=self.get_csrftoken('courier-receive'),
                                         follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_message(response.content), 'Form is invalid!')

    def test_courier_deliver(self):
        response = self.csrf_client.post(reverse('courier-deliver'),
                                         {'shipment_id': 13, 'check_code_put': '7283'},
                                         HTTP_X_CSRFTOKEN=self.get_csrftoken('courier-deliver'),
                                         follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_message(response.content), '')

    def test_courier_deliver_no_id(self):
        response = self.csrf_client.post(reverse('courier-deliver'),
                                         {'check_code_put': '7283'},
                                         HTTP_X_CSRFTOKEN=self.get_csrftoken('courier-deliver'),
                                         follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_message(response.content), 'Form is invalid!')

    def test_courier_deliver_no_checkcode(self):
        response = self.csrf_client.post(reverse('courier-deliver'),
                                         {'shipment_id': 13},
                                         HTTP_X_CSRFTOKEN=self.get_csrftoken('courier-deliver'),
                                         follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_message(response.content), 'Form is invalid!')

    def test_courier_deliver_pickup(self):
        response = self.csrf_client.post(reverse('courier-deliver'),
                                         {'shipment_id': 12, 'check_code_put': '0407'},
                                         HTTP_X_CSRFTOKEN=self.get_csrftoken('courier-deliver'),
                                         follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_message(response.content), 'Error delivering shipment: Data inconsistence detected!')

    def test_courier_deliver_wrong_code(self):
        response = self.csrf_client.post(reverse('courier-deliver'),
                                         {'shipment_id': 13, 'check_code_put': '9999'},
                                         HTTP_X_CSRFTOKEN=self.get_csrftoken('courier-deliver'),
                                         follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_message(response.content), 'Error delivering shipment: Check code incorrect!')

    def test_courier_delivered(self):
        response = self.csrf_client.get(reverse('courier-delivered'))
        self.assertEqual(response.status_code, 200)
