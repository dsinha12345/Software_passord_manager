from django.test import TestCase
from users.models import Account  
from django.urls import reverse
# Create your tests here.
class PasswordManagerTests(TestCase):

    def setUp(self):
        # Setup a test account
        self.account = Account.objects.create(username='test_account', password='old_password')

    def test_select_account(self):
        # Test selecting an account (example)
        response = self.client.get(reverse('select_account', args=['test_account']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test_account')

    def test_change_password(self):
        # Test changing a password (example)
        response = self.client.post(reverse('change_password', args=['test_account']), {
            'password': 'new_password'
        })
        self.assertEqual(response.status_code, 200)
        self.account.refresh_from_db()
        self.assertEqual(self.account.password, 'new_password')

    def test_quit_application(self):
        # Test quitting the password manager (example)
        response = self.client.get(reverse('quit'))
        self.assertEqual(response.status_code, 200)