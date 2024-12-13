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
    path('generate_password/', views.password_generator_view, name='generate_password'),
    path('account/', views.account_view, name='account'),
    path('account/change-email/', views.change_email, name='change_email'),
    path('account/change-password/', views.change_password, name='change_password'),
    path('account/delete/', views.delete_account, name='delete_account'),    
    path('view-password/<int:password_id>/', views.view_password, name='view_password'),
]

