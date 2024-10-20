from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Password  # Import the Password model

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class PasswordForm(forms.ModelForm):
    class Meta:
        model = Password
        fields = ['service_name', 'service_url', 'username', 'password']  # Updated fields
        widgets = {
            'password': forms.PasswordInput(),  # Mask the password field for security
        }
