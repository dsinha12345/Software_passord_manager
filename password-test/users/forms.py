from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Password  # Import the Password model

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Enter your password'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirm your password'}),
        }

class PasswordForm(forms.ModelForm):
    class Meta:
        model = Password
        fields = ['service_name', 'service_url', 'username', 'password']  # Updated fields
        widgets = {
            'password': forms.PasswordInput(),  # Mask the password field for security
        }

class EmailChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        
