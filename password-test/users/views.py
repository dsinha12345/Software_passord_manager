# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm, PasswordForm
from .models import Password
from django.contrib.auth.decorators import login_required

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
