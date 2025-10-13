"""
Organization models for the EPMS system.

This module contains models for departments, teams, and
organizational hierarchy management.
"""

from django.db import models
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _


class Department(models.Model):
    """
    Department model for organizational structure.
    
    Represents departments within the organization with
    hierarchical relationships and management structure.
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        validators=[MinLengthValidator(2)],
        help_text='Department name'
    )
    
    code = models.CharField(
        max_length=10,
        unique=True,
        validators=[MinLengthValidator(2)],
        help_text='Department code (e.g., HR, IT, SALES)'
    )
    
    description = models.TextField(
        blank=True,
        help_text='Department description'
    )
    
    parent_department = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_departments',
        help_text='Parent department in the hierarchy'
    )
    
    manager = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments',
        help_text='Department manager'
    )
    
    budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Department budget'
    )
    
    location = models.CharField(
        max_length=200,
        blank=True,
        help_text='Physical location of the department'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether the department is active'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for Department model."""
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ['name']
    
    def __str__(self):
        """String representation of the department."""
        return self.name
    
    @property
    def employee_count(self):
        """Get the number of employees in this department."""
        return self.employees.filter(status='active').count()
    
    @property
    def sub_department_count(self):
        """Get the number of sub-departments."""
        return self.sub_departments.filter(is_active=True).count()
    
    def get_all_sub_departments(self):
        """Get all sub-departments recursively."""
        sub_deps = list(self.sub_departments.filter(is_active=True))
        for sub_dep in self.sub_departments.filter(is_active=True):
            sub_deps.extend(sub_dep.get_all_sub_departments())
        return sub_deps
    
    def get_all_employees(self):
        """Get all employees in this department and sub-departments."""
        from accounts.models import User
        
        employees = list(self.employees.filter(status='active'))
        for sub_dep in self.get_all_sub_departments():
            employees.extend(sub_dep.employees.filter(status='active'))
        return employees


class Team(models.Model):
    """
    Team model for smaller organizational units.
    
    Represents teams within departments for more granular
    organizational structure.
    """
    
    name = models.CharField(
        max_length=100,
        help_text='Team name'
    )
    
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='teams',
        help_text='Department this team belongs to'
    )
    
    description = models.TextField(
        blank=True,
        help_text='Team description'
    )
    
    team_lead = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_teams',
        help_text='Team lead'
    )
    
    members = models.ManyToManyField(
        'accounts.User',
        through='TeamMembership',
        related_name='teams',
        help_text='Team members'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether the team is active'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for Team model."""
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'
        ordering = ['name']
        unique_together = ['name', 'department']
    
    def __str__(self):
        """String representation of the team."""
        return f"{self.name} ({self.department.name})"
    
    @property
    def member_count(self):
        """Get the number of active team members."""
        return self.members.filter(teammembership__is_active=True).count()


class TeamMembership(models.Model):
    """
    Through model for team membership.
    
    Represents the relationship between users and teams
    with additional metadata.
    """
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        help_text='Team member'
    )
    
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        help_text='Team'
    )
    
    role = models.CharField(
        max_length=50,
        default='member',
        help_text='Role in the team'
    )
    
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(
        default=True,
        help_text='Whether the membership is active'
    )
    
    class Meta:
        """Meta options for TeamMembership model."""
        verbose_name = 'Team Membership'
        verbose_name_plural = 'Team Memberships'
        unique_together = ['user', 'team']
    
    def __str__(self):
        """String representation of the team membership."""
        return f"{self.user.employee_id} in {self.team.name}"


class Position(models.Model):
    """
    Position model for job positions.
    
    Represents job positions within the organization
    with associated requirements and responsibilities.
    """
    
    title = models.CharField(
        max_length=100,
        help_text='Job title'
    )
    
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='positions',
        help_text='Department this position belongs to'
    )
    
    description = models.TextField(
        help_text='Job description'
    )
    
    requirements = models.TextField(
        blank=True,
        help_text='Job requirements'
    )
    
    responsibilities = models.TextField(
        blank=True,
        help_text='Job responsibilities'
    )
    
    level = models.CharField(
        max_length=20,
        choices=[
            ('entry', 'Entry Level'),
            ('mid', 'Mid Level'),
            ('senior', 'Senior Level'),
            ('lead', 'Lead'),
            ('manager', 'Manager'),
            ('director', 'Director'),
            ('executive', 'Executive'),
        ],
        default='mid',
        help_text='Position level'
    )
    
    min_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Minimum salary for this position'
    )
    
    max_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Maximum salary for this position'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether the position is active'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for Position model."""
        verbose_name = 'Position'
        verbose_name_plural = 'Positions'
        ordering = ['title']
        unique_together = ['title', 'department']
    
    def __str__(self):
        """String representation of the position."""
        return f"{self.title} ({self.department.name})"
    
    @property
    def salary_range(self):
        """Get salary range as string."""
        if self.min_salary and self.max_salary:
            return f"${self.min_salary:,.2f} - ${self.max_salary:,.2f}"
        elif self.min_salary:
            return f"${self.min_salary:,.2f}+"
        elif self.max_salary:
            return f"Up to ${self.max_salary:,.2f}"
        return "Not specified"