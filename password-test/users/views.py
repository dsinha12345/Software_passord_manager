# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm, PasswordForm
from .models import Password
from django.contrib.auth.decorators import login_required
from django.views import View
import os
import google.generativeai as genai

genai.configure(api_key=os.environ.get("API_KEY"))

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirect to the password dashboard
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def home(request):
    return render(request, 'users/home.html')

@login_required
def dashboard(request):
    passwords = Password.objects.filter(user=request.user)
    return render(request, 'users/dashboard.html', {'passwords': passwords})

@login_required
def edit_password(request, id):
    password_instance = get_object_or_404(Password, id=id, user=request.user)
    if request.method == 'POST':
        form = PasswordForm(request.POST, instance=password_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password updated successfully!')
            return redirect('dashboard')
    else:
        form = PasswordForm(instance=password_instance)
    return render(request, 'users/password_form.html', {'form': form})

@login_required
def delete_password(request, id):
    password_instance = get_object_or_404(Password, id=id, user=request.user)
    if request.method == 'POST':
        password_instance.delete()
        messages.success(request, 'Password deleted successfully!')
        return redirect('dashboard')
    return render(request, 'users/delete_password.html', {'password': password_instance})

@login_required
def add_password_view(request):
    if request.method == 'POST':
        form = PasswordForm(request.POST)
        if form.is_valid():
            password_instance = form.save(commit=False)  # Create the object but don't save it yet
            password_instance.user = request.user  # Assign the logged-in user
            password_instance.save()  # Now save the object
            messages.success(request, 'Password added successfully!')
            return redirect('dashboard')  # Redirect to the password dashboard
    else:
        form = PasswordForm()

    return render(request, 'users/add_password.html', {'form': form})
@login_required
def password_generator_view(request):
    # Initialize chat_history from session, or create a new list if it doesn't exist
    chat_history = request.session.get('chat_history', [])
    bot_response = None
    
    if request.method == 'POST':
        user_message = request.POST.get('user_message')
        
        # Add user's message to chat history
        chat_history.append({'user': 'You', 'text': user_message})
        
        try:
            # Generate a response using the Google Generative AI Gemini model
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(user_message)
            bot_response = response.text  # Extract the response text
            
            # Add bot response to chat history
            chat_history.append({'user': 'Bot', 'text': bot_response})
        except Exception as e:
            bot_response = f"Sorry, I encountered an error: {str(e)}"

        # Save updated chat_history back to session
        request.session['chat_history'] = chat_history

    context = {
        'chat_history': chat_history,
        'bot_response': bot_response
    }
    
    return render(request, 'users/generate_password.html', context)


class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        # Clear all messages in the session
        storage = messages.get_messages(request)
        storage.used = True  # Mark existing messages as used
        storage._loaded = False  # Reset the loaded state to clear messages

        logout(request)  # Log the user out
        messages.success(request, "You have been logged out successfully.")  # Optional message
        return redirect('home')  # Redirect to the home page or any other page
