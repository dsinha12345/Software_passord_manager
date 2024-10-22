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
import html  # To escape special characters
from django.http import JsonResponse

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

def initialize_model(system_instruction):
    return genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_instruction)

@login_required
def password_generator_view(request):
    chat_history = request.session.get('chat_history', [])
    bot_response = None

    if request.method == 'POST':
        user_message = request.POST.get('user_message', '').strip()

        if user_message:  
            # Prepare the message with formatting instructions
            formatted_message = f"""
            X:

            ** Password Suggestions related to the X: **

            **Easy to Remember:**
            * **[Password 1]**
            * **[Password 2]**
            * **[Password 3]**

            **More Secure (using symbols and numbers):**
            * **[Password 4]**
            * **[Password 5]**

            **Unique and Specific:**
            * **[Password 6]**
            * **[Password 7]**

            **Tips for Strong Passwords:**
            * **[Tip 1]**
            * **[Tip 2]**

            **Remember:**
            * **[Reminder 1]**
            * **[Reminder 2]**
            """

            # Append the user message to chat history
            chat_history.append({'user': 'You', 'text': format_message(user_message)})

            try:
                # Initialize the model with the correct system_instruction
                model = initialize_model(formatted_message)
                response = model.generate_content(user_message)
                print(response)
                bot_response = response.text  

                # Check if response is in expected format
                if response.text:
                    formatted_response = format_message(bot_response)
                    chat_history.append({'user': 'Bot', 'text': formatted_response})
                else:
                    bot_response = "No valid response generated."
                    chat_history.append({'user': 'Bot', 'text': format_message(bot_response)})
                    
            except Exception as e:
                # More specific exception handling
                bot_response = f"Sorry, I encountered an error while processing your request: {str(e)}"
                formatted_response = format_message(bot_response)
                chat_history.append({'user': 'Bot', 'text': formatted_response})

        else:
            # If user input is empty, return a 400 Bad Request response
            return JsonResponse({
                'error': 'User message is required. Please enter a valid message.'
            }, status=400)

        # Save the updated chat history back to the session
        request.session['chat_history'] = chat_history

    # Initialize bot_response for the initial GET request
    context = {
        'chat_history': chat_history,
        'bot_response': bot_response or "Welcome to BeeSafe! Please enter your message."
    }

    return render(request, 'users/generate_password.html', context)

import html

def format_message(text):
    lines = text.split('\n')
    formatted_text = ""
    in_list = False  # Track whether we're inside a list

    for line in lines:
        line = line.strip()  # Clean any extra spaces

        # Check if the line is a list item (starts with "* ")
        if line.startswith("* ") and not line[2:].startswith("*"):
            if not in_list:
                formatted_text += "<ul>\n"  # Start a new unordered list
                in_list = True

            # Handle bold text within list items
            if "**" in line:
                start_idx = line.find("**")
                end_idx = line.rfind("**")
                bold_text = line[start_idx + 2:end_idx]
                before_bold = html.escape(line[2:start_idx])
                after_bold = html.escape(line[end_idx + 2:])

                formatted_text += f"<li>{before_bold.strip()}<b>{bold_text.strip()}</b>{after_bold.strip()}</li>\n"
            else:
                formatted_text += f"<li>{html.escape(line[2:].strip())}</li>\n"

        # Handle section headings or regular text
        elif line.startswith("##") or line.startswith("**"):
            if in_list:
                formatted_text += "</ul>\n"  # Close the unordered list
                in_list = False
            formatted_text += f"<p><b>{html.escape(line.strip())}</b></p>\n"

        else:
            if in_list:
                formatted_text += "</ul>\n"  # Close the unordered list if it was open
                in_list = False
            formatted_text += f"<p>{html.escape(line.strip())}</p>\n"

    # Ensure any open list is closed at the end
    if in_list:
        formatted_text += "</ul>\n"

    return formatted_text



class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        # Clear all messages in the session
        storage = messages.get_messages(request)
        storage.used = True  # Mark existing messages as used
        storage._loaded = False  # Reset the loaded state to clear messages

        logout(request)  # Log the user out
        messages.success(request, "You have been logged out successfully.")  # Optional message
        return redirect('home')  # Redirect to the home page or any other page
