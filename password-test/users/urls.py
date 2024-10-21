# users/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add_password/', views.add_password_view, name='add_password'),
    path('edit_password/<int:id>/', views.edit_password, name='edit_password'),
    path('delete_password/<int:id>/', views.delete_password, name='delete_password'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'), 
    # path('generate-password/', views.password_generator_view, name='generate-password'),
]
