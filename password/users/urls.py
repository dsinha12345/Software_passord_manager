# users/urls.py
from django.urls import path, include
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    #path('', include('password_generator.urls')),  # Include the password_generator app URLs
]
