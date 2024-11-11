# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm, PasswordForm, VerifyUserPasswordForm
from .models import Password
from django.contrib.auth.decorators import login_required
from django.views import View
from datetime import datetime
import os
import google.generativeai as genai
import html  # To escape special characters
from django.http import JsonResponse
import html
import re

genai.configure(api_key=os.environ.get("AIzaSyDkc_ZX6AwRxG8rWp32sTH5OmOuD-x2fZo"))

def verify_user_password(view_func):
    def wrapper(request, *args, **kwargs):
        # Store the original path and method in session
        request.session['intended_path'] = request.path
        request.session['intended_method'] = request.method
        
        if 'verified_for_path' in request.session and request.session['verified_for_path'] == request.path:
            # Clear the verification after use
            del request.session['verified_for_path']
            return view_func(request, *args, **kwargs)
            
        if request.method == 'POST':
            if 'verify_password' in request.POST:
                verification_form = VerifyUserPasswordForm(request.POST)
                if verification_form.is_valid():
                    entered_password = verification_form.cleaned_data['password']
                    if check_password(entered_password, request.user.password):
                        request.session['verified_for_path'] = request.path
                        return redirect(request.path)
                    else:
                        messages.error(request, 'Incorrect password. Please try again.')
                        return render(request, 'users/verify_password.html', {
                            'form': verification_form,
                            'next_url': request.path
                        })
            
        # Show verification form
        verification_form = VerifyUserPasswordForm(initial={'next_action': request.path})
        return render(request, 'users/verify_password.html', {
            'form': verification_form,
            'next_url': request.path
        })
    
    return wrapper




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
@verify_user_password
def edit_password(request, id):
    password_instance = get_object_or_404(Password, id=id, user=request.user)
    if request.method == 'POST':
        form = PasswordForm(request.POST, instance=password_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password updated successfully!')
            # Clear any remaining verification
            request.session.pop('verified_for_path', None)
            return redirect('dashboard')
    else:
        # For GET requests, show the form with existing data
        form = PasswordForm(instance=password_instance)
    
    return render(request, 'users/password_form.html', {'form': form})

@login_required
@verify_user_password
def delete_password(request, id):
    password_instance = get_object_or_404(Password, id=id, user=request.user)
    if request.method == 'POST':
        if 'confirm_delete' in request.POST:
            password_instance.delete()
            messages.success(request, 'Password deleted successfully!')
            # Clear any remaining verification
            request.session.pop('verified_for_path', None)
            return redirect('dashboard')
    
    # Show confirmation page
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

def initialize_model(system_instruction):
    return genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_instruction)

@login_required
def password_generator_view(request):
    chat_history = request.session.get('chat_history', [])
    
    # Handle AJAX POST request
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        user_message = request.POST.get('user_message', '').strip()
        
        if not user_message:
            return JsonResponse({
                'status': 'error',
                'message': 'User message is required. Please enter a valid message.'
            }, status=400)

        try:
            # Prepare the message with formatting instructions
            formatted_message = f"""Based on the topic "{user_message}", here are personalized password suggestions:

🔑 Easy to Remember
* {user_message}-inspired simple passwords:
  - [Strong Password 1]
  - [Strong Password 2]
  - [Strong Password 3]

🛡️ Enhanced Security
* Complex variations with symbols & numbers:
  - [Complex Password 1]
  - [Complex Password 2]

🎯 Unique & Topic-Specific
* Specialized combinations:
  - [Unique Password 1]
  - [Unique Password 2]

📝 Security Tips
* [Specific tip related to password structure]
* [Specific tip related to password management]

⚠️ Important Reminders
* Never reuse passwords across different accounts
* Store passwords securely using a password manager
"""
            # Generate response using the model
            model = initialize_model(formatted_message)
            response = model.generate_content(user_message)
            
            if response.text:
                bot_response = format_message(response.text)
                # Update session chat history
                chat_history.append({'user': 'You', 'text': format_message(user_message)})
                chat_history.append({'user': 'Bot', 'text': bot_response})
                request.session['chat_history'] = chat_history
                
                return JsonResponse({
                    'status': 'success',
                    'bot_response': bot_response
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No valid response generated.'
                }, status=500)
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error processing request: {str(e)}'
            }, status=500)

    # Handle regular GET request
    context = {
        'chat_history': chat_history,
    }
    return render(request, 'users/generate_password.html', context)

def format_message(text):
    """
    Format the message with proper HTML structure, handling:
    - Emojis
    - Multiple levels of lists
    - Section headers with emojis
    - Bold text
    - Regular paragraphs
    """
    if not text:
        return ""

    lines = text.split('\n')
    formatted_text = []
    in_list = False
    in_nested_list = False
    
    for line in lines:
        line = line.strip()
        if not line:  # Handle empty lines
            if in_nested_list:
                formatted_text.append("  </ul>")
                in_nested_list = False
            if in_list:
                formatted_text.append("</ul>")
                in_list = False
            formatted_text.append("<br>")
            continue

        # Handle section headers (lines with emojis)
        if re.match(r'^[🔑🛡️🎯📝⚠️]', line):
            if in_nested_list:
                formatted_text.append("  </ul>")
                in_nested_list = False
            if in_list:
                formatted_text.append("</ul>")
                in_list = False
            formatted_text.append(f'<h3 class="password-section">{html.escape(line)}</h3>')
            continue

        # Handle main bullet points
        if line.startswith('* '):
            if not in_list:
                formatted_text.append('<ul class="password-list">')
                in_list = True
            
            content = line[2:].strip()
            # Check if it's a category description
            if content.endswith(':'):
                formatted_text.append(f'<li class="category"><strong>{html.escape(content)}</strong></li>')
            else:
                formatted_text.append(f'<li>{html.escape(content)}</li>')
            continue

        # Handle nested bullet points (indented with -)
        if line.startswith('  - '):
            if not in_nested_list:
                formatted_text.append('  <ul class="nested-password-list">')
                in_nested_list = True
            
            content = line[4:].strip()
            # Process bold text within brackets
            content = re.sub(r'\[(.*?)\]', r'<strong>\1</strong>', html.escape(content))
            formatted_text.append(f'    <li>{content}</li>')
            continue

        # Handle regular text
        if in_nested_list:
            formatted_text.append("  </ul>")
            in_nested_list = False
        if in_list:
            formatted_text.append("</ul>")
            in_list = False
        
        # Process bold text wrapped in square brackets or asterisks
        line = re.sub(r'\[(.*?)\]', r'<strong>\1</strong>', html.escape(line))
        line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
        formatted_text.append(f'<p>{line}</p>')

    # Close any open lists
    if in_nested_list:
        formatted_text.append("  </ul>")
    if in_list:
        formatted_text.append("</ul>")

    return '\n'.join(formatted_text)



class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        # Clear all messages in the session
        storage = messages.get_messages(request)
        storage.used = True  # Mark existing messages as used
        storage._loaded = False  # Reset the loaded state to clear messages

        logout(request)  # Log the user out
        messages.success(request, "You have been logged out successfully.")  # Optional message
        return redirect('home')  # Redirect to the home page or any other page
