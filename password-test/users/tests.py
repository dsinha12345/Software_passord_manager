from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Password
from .forms import UserRegisterForm, PasswordForm
import google.generativeai as genai
from unittest.mock import patch, MagicMock
from users.views import password_generator_view
from bs4 import BeautifulSoup

User = get_user_model()

class UserViewsTestCase(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password@123')

    def test_register_view(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'password@123',
            'password2': 'password@123',
        })
        self.assertEqual(response.status_code, 302)  # Expect a redirect on successful registration
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_view_password_without_special_characters(self):
        response = self.client.post(reverse('register'), {
            'username': 'invaliduser',
            'email': 'invaliduser@example.com',
            'password1': 'password123',  # Invalid password (no special character)
            'password2': 'password123',
        })
        self.assertEqual(response.status_code, 200)  # Expect to stay on the registration page
        self.assertFalse(User.objects.filter(username='invaliduser').exists())

    def test_register_view_incorrect_email_format(self):
        response = self.client.post(reverse('register'), {
            'username': 'invaliduser',
            'email': 'invaliduser@example', #invalid email format
            'password1': 'password123',  
            'password2': 'password123',
        })
        self.assertEqual(response.status_code, 200)  # Expect to stay on the registration page
        self.assertFalse(User.objects.filter(username='invaliduser').exists())

    def test_login_view(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'password@123',
        })
        self.assertEqual(response.status_code, 302)  # Expect a redirect after successful login
        self.assertEqual(str(response.wsgi_request.user), 'testuser')  # Check if user is logged in

    def test_login_view_user_not_exist(self):
        response = self.client.post(reverse('login'), {
            'username': 'nonexistentuser',  # Username that does not exist
            'password': 'password@123',       # Any password
        })
        self.assertEqual(response.status_code, 200)  # Stay on the login page
        self.assertContains(response, "Invalid username or password.")  # Check for error message
        
    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)  # Expect a successful response

    def test_dashboard_view(self):
        self.client.login(username='testuser', password='password@123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)  # Expect a successful response

    def test_add_password_view(self):
        self.client.login(username='testuser', password='password@123')
        response = self.client.post(reverse('add_password'), {
            'service_name': 'Example Service',
            'service_url': 'https://example.com',
            'username': 'exampleuser',
            'password': 'examplepassword',
        })
        self.assertEqual(response.status_code, 302)  # Expect a redirect after adding password
        self.assertTrue(Password.objects.filter(service_name='Example Service').exists())


    def test_edit_password_view(self):
        self.client.login(username='testuser', password='password@123')
        password_instance = Password.objects.create(
            user=self.user,
            service_name='Example Service',
            service_url='https://example.com',
            username='exampleuser',
            password='examplepassword'
        )
        response = self.client.post(reverse('edit_password', args=[password_instance.id]), {
            'service_name': 'Updated Service',
            'service_url': 'https://updatedexample.com',
            'username': 'updateduser',
            'password': 'updatedpassword',
        })
        self.assertEqual(response.status_code, 302)  # Expect a redirect after editing password
        password_instance.refresh_from_db()
        self.assertEqual(password_instance.service_name, 'Updated Service')


    def test_delete_password_view(self):
        self.client.login(username='testuser', password='password@123')
        password_instance = Password.objects.create(
            user=self.user,
            service_name='Example Service',
            service_url='https://example.com',
            username='exampleuser',
            password='examplepassword'
        )
        response = self.client.post(reverse('delete_password', args=[password_instance.id]))
        self.assertEqual(response.status_code, 302)  # Expect a redirect after deleting password
        self.assertFalse(Password.objects.filter(id=password_instance.id).exists())

    @patch('users.views.initialize_model')
    def test_successful_user_message_processing(self, mock_initialize_model):
        self.client.login(username='testuser', password='password@123')

        # Mock the model's response
        mock_model_instance = mock_initialize_model.return_value
        mock_model_instance.generate_content.return_value = MagicMock(text='Generated password: applePie')

        # Simulate POST request with 'user_message'
        response = self.client.post(reverse('generate_password'), {'user_message': 'fruits'})

        # Assertions
        self.assertEqual(response.status_code, 200)

        # Parse the response content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the user's message
        user_message_div = soup.find('div', class_='message you-message')
        self.assertIsNotNone(user_message_div)
        self.assertIn('fruits', user_message_div.get_text())

        # Find the bot's message
        bot_message_div = soup.find('div', class_='message bot-message')
        self.assertIsNotNone(bot_message_div)
        self.assertIn('Generated password: applePie', bot_message_div.get_text())

        # Check that the chat history is saved in the session
        chat_history = self.client.session.get('chat_history')
        self.assertEqual(len(chat_history), 2)  # User and bot messages

    @patch('users.views.initialize_model')
    def test_user_message_processing_failure_due_to_missing_input(self, mock_initialize_model):
        self.client.login(username='testuser', password='password@123')

        mock_model_instance = mock_initialize_model.return_value
        mock_model_instance.generate_content.return_value = MagicMock(text='Generated password: applePie')

        # Simulate POST request with missing 'user_message'
        response = self.client.post(reverse('generate_password'), {'user_message': ''})

        # Assertions
        self.assertEqual(response.status_code, 400)  # Expecting a Bad Request status
        self.assertContains(response, 'User message is required. Please enter a valid message.', status_code=400)