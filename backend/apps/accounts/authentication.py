"""
Custom authentication backends for the accounts app.

This module contains custom authentication backends that extend
Django's default authentication to support email-based login.
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to authenticate
    using either their username or email address.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """Authenticate user using username or email."""
        if username is None or password is None:
            return None
        
        try:
            # Try to find user by email first
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            try:
                # Try to find user by username
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None
        
        # Check if the user is active
        if not user.is_active:
            return None
        
        # Check the password
        if user.check_password(password):
            return user
        
        return None
    
    def get_user(self, user_id):
        """Get user by ID."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
