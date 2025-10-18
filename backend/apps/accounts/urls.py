"""
URL configuration for the accounts app.

This module defines the URL patterns for user authentication,
registration, and profile management endpoints.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from . import csv_views
from . import health_views

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.logout_view, name='logout'),
    
    # User registration
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    
    # User profile management
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/extended/', views.UserProfileExtendedView.as_view(), name='profile_extended'),
    
    # User management
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:id>/', views.UserDetailView.as_view(), name='user_detail'),
    
    # Password management
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('reset-password/', views.PasswordResetView.as_view(), name='reset_password'),
    
    # Employee Dashboard endpoints
    path('dashboard/', views.get_employee_dashboard_data, name='employee_dashboard'),
    path('dashboard/progress/', views.get_employee_progress_summary, name='employee_progress'),
    path('dashboard/action-items/', views.get_employee_action_items, name='employee_action_items'),
    
    # CSV Import endpoints
    path('csv/upload/', csv_views.CSVUploadValidateView.as_view(), name='csv_upload'),
    path('csv/import/', csv_views.CSVImportConfirmView.as_view(), name='csv_import'),
    path('csv/template/', csv_views.CSVTemplateDownloadView.as_view(), name='csv_template'),
    
    # Health check endpoints
    path('health/', health_views.health_check, name='health_check'),
    path('health/readiness/', health_views.readiness_check, name='readiness_check'),
    path('health/liveness/', health_views.liveness_check, name='liveness_check'),
]