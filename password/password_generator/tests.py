from django.test import TestCase
from django.urls import reverse
import string

# Create your tests here.
class PasswordGeneratorTest(TestCase):

    def test_default_password_length(self):
        """Test password generation with default length."""
        response = self.client.get(reverse('generate_password'))
        password = response.context['password']
        self.assertEqual(len(password), 12)
    
    def test_custom_password_length(self):
        """Test password generation with a custom length."""
        response = self.client.get(reverse('generate_password'), {'length': 16})
        password = response.context['password']
        self.assertEqual(len(password), 16)
    
    def test_minimum_password_length(self):
        """Test password generation with minimum length."""
        response = self.client.get(reverse('generate_password'), {'length': 8})
        password = response.context['password']
        self.assertEqual(len(password), 8)

    def test_maximum_password_length(self):
        """Test password generation with maximum length."""
        response = self.client.get(reverse('generate_password'), {'length': 64})
        password = response.context['password']
        self.assertEqual(len(password), 64)

    def test_password_with_uppercase(self):
        """Test password generation with uppercase letters."""
        response = self.client.get(reverse('generate_password'), {'uppercase': 'on'})
        password = response.context['password']
        self.assertTrue(any(char in string.ascii_uppercase for char in password))

    def test_password_with_numbers(self):
        """Test password generation with numbers."""
        response = self.client.get(reverse('generate_password'), {'numbers': 'on'})
        password = response.context['password']
        self.assertTrue(any(char in string.digits for char in password))

    def test_password_with_special_characters(self):
        """Test password generation with special characters."""
        response = self.client.get(reverse('generate_password'), {'special': 'on'})
        password = response.context['password']
        self.assertTrue(any(char in string.punctuation for char in password))

    def test_password_with_all_options(self):
        """Test password generation with all options enabled."""
        response = self.client.get(reverse('generate_password'), {
            'length': 20,
            'uppercase': 'on',
            'numbers': 'on',
            'special': 'on'
        })
        password = response.context['password']
        self.assertEqual(len(password), 20)
        self.assertTrue(any(char in string.ascii_uppercase for char in password))
        self.assertTrue(any(char in string.digits for char in password))
        self.assertTrue(any(char in string.punctuation for char in password))
