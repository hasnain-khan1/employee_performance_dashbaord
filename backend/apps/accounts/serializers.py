"""
Serializers for the accounts app.

This module contains DRF serializers for user authentication,
registration, and profile management.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    
    Handles user creation with password validation and
    employee ID generation.
    """
    
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        help_text='User password (must meet security requirements)'
    )
    password_confirm = serializers.CharField(
        write_only=True,
        help_text='Password confirmation'
    )
    
    class Meta:
        """Meta options for UserRegistrationSerializer."""
        model = User
        fields = [
            'employee_id', 'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'role', 'phone', 'hire_date',
            'department', 'job_title', 'bio'
        ]
        extra_kwargs = {
            'employee_id': {'read_only': True},
            'role': {'default': 'employee'},
        }
    
    def validate(self, attrs):
        """Validate the registration data."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def create(self, validated_data):
        """Create a new user."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Generate employee ID if not provided
        if not validated_data.get('employee_id'):
            last_user = User.objects.filter(
                employee_id__startswith='EMP'
            ).order_by('-employee_id').first()
            
            if last_user:
                last_id = int(last_user.employee_id[3:])
                new_id = f"EMP{last_id + 1:06d}"
            else:
                new_id = "EMP000001"
            
            validated_data['employee_id'] = new_id
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information.
    
    Handles extended profile data including personal information,
    skills, and preferences.
    """
    
    skills_list = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
        help_text='List of user skills'
    )
    
    class Meta:
        """Meta options for UserProfileSerializer."""
        model = UserProfile
        fields = [
            'date_of_birth', 'address', 'emergency_contact_name',
            'emergency_contact_phone', 'skills', 'skills_list',
            'certifications', 'education', 'timezone', 'language',
            'notification_preferences'
        ]
    
    def update(self, instance, validated_data):
        """Update user profile."""
        # Handle skills list if provided
        if 'skills_list' in self.initial_data:
            skills = self.initial_data['skills_list']
            if isinstance(skills, list):
                instance.skills = ', '.join(skills)
        
        return super().update(instance, validated_data)


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user information.
    
    Provides user data for API responses with related
    profile information.
    """
    
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    manager_name = serializers.CharField(
        source='manager.get_full_name',
        read_only=True
    )
    department_name = serializers.CharField(
        source='department.name',
        read_only=True
    )
    direct_reports_count = serializers.SerializerMethodField()
    
    class Meta:
        """Meta options for UserSerializer."""
        model = User
        fields = [
            'id', 'employee_id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'status', 'phone', 'hire_date', 'manager', 'manager_name',
            'department', 'department_name', 'job_title', 'bio', 'avatar',
            'profile', 'direct_reports_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'employee_id', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        """Get full name of the user."""
        return obj.get_full_name() or f"{obj.first_name} {obj.last_name}".strip() or obj.username
    
    def get_direct_reports_count(self, obj):
        """Get count of direct reports."""
        return obj.get_direct_reports().count()


class UserListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for user lists.
    
    Used in list views where full user details are not needed.
    """
    
    full_name = serializers.SerializerMethodField()
    manager_name = serializers.CharField(
        source='manager.get_full_name',
        read_only=True
    )
    department_name = serializers.CharField(
        source='department.name',
        read_only=True
    )
    
    class Meta:
        """Meta options for UserListSerializer."""
        model = User
        fields = [
            'id', 'employee_id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'status', 'job_title', 'manager', 'manager_name', 
            'department', 'department_name', 'hire_date', 'phone', 'avatar', 'created_at'
        ]
    
    def get_full_name(self, obj):
        """Get full name of the user."""
        return obj.get_full_name() or f"{obj.first_name} {obj.last_name}".strip() or obj.username


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    
    Handles authentication credentials validation.
    """
    
    username = serializers.CharField(
        help_text='Username or email address'
    )
    password = serializers.CharField(
        write_only=True,
        help_text='User password'
    )
    
    def validate(self, attrs):
        """Validate login credentials."""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            # Try to authenticate with username or email
            user = authenticate(
                username=username,
                password=password
            )
            
            if not user:
                # Try with email if username failed
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(
                        username=user_obj.username,
                        password=password
                    )
                except User.DoesNotExist:
                    pass
            
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('User account is disabled.')
                attrs['user'] = user
                return attrs
            else:
                raise serializers.ValidationError('Invalid credentials.')
        else:
            raise serializers.ValidationError('Must include username and password.')


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change.
    
    Handles password change with validation.
    """
    
    old_password = serializers.CharField(
        write_only=True,
        help_text='Current password'
    )
    new_password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        help_text='New password (must meet security requirements)'
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        help_text='New password confirmation'
    )
    
    def validate(self, attrs):
        """Validate password change data."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match.")
        return attrs
    
    def validate_old_password(self, value):
        """Validate the old password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for password reset request.
    
    Handles password reset email sending.
    """
    
    email = serializers.EmailField(
        help_text='Email address associated with the account'
    )
    
    def validate_email(self, value):
        """Validate email exists."""
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('No account found with this email address.')
        return value