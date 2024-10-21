from django.urls import path
from . import views

urlpatterns = [
    path('password_generator/', views.generate_password, name='password_generator'),
]