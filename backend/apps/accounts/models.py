"""
User and authentication models for the EPMS system.

This module contains the custom User model and related authentication
models that extend Django's built-in user system.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model for EPMS.
    
    Extends Django's AbstractUser to include additional fields
    specific to the employee performance management system.
    """
    
    # Role choices
    ROLE_CHOICES = [
        ('employee', 'Employee'),
        ('manager', 'Manager'),
        ('hr', 'HR'),
        ('admin', 'Admin'),
    ]
    
    # Status choices
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'),
        ('terminated', 'Terminated'),
    ]
    
    # Additional fields
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        validators=[RegexValidator(
            regex=r'^EMP\d{6}$',
            message='Employee ID must be in format EMP000000'
        )],
        help_text='Unique employee identifier (e.g., EMP000001)'
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='employee',
        help_text='User role in the system'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text='Current employment status'
    )
    
    phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message='Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.'
        )],
        help_text='Contact phone number'
    )
    
    hire_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date when the employee was hired'
    )
    
    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='direct_reports',
        help_text='Direct manager of this employee'
    )
    
    department = models.ForeignKey(
        'org.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        help_text='Department this employee belongs to'
    )
    
    job_title = models.CharField(
        max_length=100,
        blank=True,
        help_text='Current job title'
    )
    
    bio = models.TextField(
        blank=True,
        help_text='Short biography or description'
    )
    
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        help_text='Profile picture'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for User model."""
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['employee_id']
    
    def __str__(self):
        """String representation of the user."""
        return f"{self.employee_id} - {self.get_full_name()}"
    
    @property
    def full_name(self):
        """Return the user's full name."""
        return self.get_full_name()
    
    @property
    def is_manager(self):
        """Check if user is a manager."""
        return self.role in ['manager', 'hr', 'admin']
    
    @property
    def is_hr(self):
        """Check if user is HR."""
        return self.role in ['hr', 'admin']
    
    @property
    def is_admin(self):
        """Check if user is admin."""
        return self.role == 'admin'
    
    def get_direct_reports(self):
        """Get all direct reports for this user."""
        return self.direct_reports.filter(status='active')
    
    def get_all_reports(self):
        """Get all reports (direct and indirect) for this user."""
        reports = list(self.get_direct_reports())
        for report in self.get_direct_reports():
            reports.extend(report.get_all_reports())
        return reports


class UserProfile(models.Model):
    """
    Extended user profile information.
    
    Contains additional profile information that doesn't need to be
    in the main User model for performance reasons.
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    # Personal information
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text='Date of birth'
    )
    
    address = models.TextField(
        blank=True,
        help_text='Home address'
    )
    
    emergency_contact_name = models.CharField(
        max_length=100,
        blank=True,
        help_text='Emergency contact name'
    )
    
    emergency_contact_phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message='Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.'
        )],
        help_text='Emergency contact phone number'
    )
    
    # Professional information
    skills = models.TextField(
        blank=True,
        help_text='Comma-separated list of skills'
    )
    
    certifications = models.TextField(
        blank=True,
        help_text='Professional certifications'
    )
    
    education = models.TextField(
        blank=True,
        help_text='Educational background'
    )
    
    # Preferences
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        help_text='User timezone'
    )
    
    language = models.CharField(
        max_length=10,
        default='en',
        help_text='Preferred language'
    )
    
    notification_preferences = models.JSONField(
        default=dict,
        help_text='User notification preferences'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for UserProfile model."""
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        """String representation of the user profile."""
        return f"Profile for {self.user.employee_id}"
    
    @property
    def skills_list(self):
        """Return skills as a list."""
        if self.skills:
            return [skill.strip() for skill in self.skills.split(',') if skill.strip()]
        return []
    
    def add_skill(self, skill):
        """Add a skill to the skills list."""
        skills = self.skills_list
        if skill not in skills:
            skills.append(skill)
            self.skills = ', '.join(skills)
            self.save()
    
    def remove_skill(self, skill):
        """Remove a skill from the skills list."""
        skills = self.skills_list
        if skill in skills:
            skills.remove(skill)
            self.skills = ', '.join(skills)
            self.save()