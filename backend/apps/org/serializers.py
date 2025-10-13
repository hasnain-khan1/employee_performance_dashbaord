"""
Serializers for the org app.

This module contains DRF serializers for organizational
structure management including departments, teams, and positions.
"""

from rest_framework import serializers
from .models import Department, Team, TeamMembership, Position


class DepartmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Department model.
    
    Handles department data with related information
    and computed fields.
    """
    
    employee_count = serializers.ReadOnlyField()
    sub_department_count = serializers.ReadOnlyField()
    manager_name = serializers.CharField(
        source='manager.get_full_name',
        read_only=True
    )
    parent_department_name = serializers.CharField(
        source='parent_department.name',
        read_only=True
    )
    
    class Meta:
        """Meta options for DepartmentSerializer."""
        model = Department
        fields = [
            'id', 'name', 'code', 'description', 'parent_department',
            'parent_department_name', 'manager', 'manager_name', 'budget',
            'location', 'is_active', 'employee_count', 'sub_department_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DepartmentListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for department lists.
    
    Used in list views where full department details are not needed.
    """
    
    manager_name = serializers.CharField(
        source='manager.get_full_name',
        read_only=True
    )
    employee_count = serializers.ReadOnlyField()
    
    class Meta:
        """Meta options for DepartmentListSerializer."""
        model = Department
        fields = [
            'id', 'name', 'code', 'manager_name', 'employee_count',
            'is_active', 'created_at'
        ]


class TeamMembershipSerializer(serializers.ModelSerializer):
    """
    Serializer for TeamMembership model.
    
    Handles team membership data with user information.
    """
    
    user_name = serializers.CharField(
        source='user.get_full_name',
        read_only=True
    )
    user_employee_id = serializers.CharField(
        source='user.employee_id',
        read_only=True
    )
    
    class Meta:
        """Meta options for TeamMembershipSerializer."""
        model = TeamMembership
        fields = [
            'id', 'user', 'user_name', 'user_employee_id', 'team',
            'role', 'joined_at', 'is_active'
        ]
        read_only_fields = ['id', 'joined_at']


class TeamSerializer(serializers.ModelSerializer):
    """
    Serializer for Team model.
    
    Handles team data with members and related information.
    """
    
    member_count = serializers.ReadOnlyField()
    team_lead_name = serializers.CharField(
        source='team_lead.get_full_name',
        read_only=True
    )
    department_name = serializers.CharField(
        source='department.name',
        read_only=True
    )
    members = TeamMembershipSerializer(
        source='teammembership_set',
        many=True,
        read_only=True
    )
    
    class Meta:
        """Meta options for TeamSerializer."""
        model = Team
        fields = [
            'id', 'name', 'department', 'department_name', 'description',
            'team_lead', 'team_lead_name', 'members', 'member_count',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TeamListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for team lists.
    
    Used in list views where full team details are not needed.
    """
    
    team_lead_name = serializers.CharField(
        source='team_lead.get_full_name',
        read_only=True
    )
    department_name = serializers.CharField(
        source='department.name',
        read_only=True
    )
    member_count = serializers.ReadOnlyField()
    
    class Meta:
        """Meta options for TeamListSerializer."""
        model = Team
        fields = [
            'id', 'name', 'department_name', 'team_lead_name',
            'member_count', 'is_active', 'created_at'
        ]


class PositionSerializer(serializers.ModelSerializer):
    """
    Serializer for Position model.
    
    Handles position data with computed fields.
    """
    
    salary_range = serializers.ReadOnlyField()
    department_name = serializers.CharField(
        source='department.name',
        read_only=True
    )
    
    class Meta:
        """Meta options for PositionSerializer."""
        model = Position
        fields = [
            'id', 'title', 'department', 'department_name', 'description',
            'requirements', 'responsibilities', 'level', 'min_salary',
            'max_salary', 'salary_range', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PositionListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for position lists.
    
    Used in list views where full position details are not needed.
    """
    
    department_name = serializers.CharField(
        source='department.name',
        read_only=True
    )
    salary_range = serializers.ReadOnlyField()
    
    class Meta:
        """Meta options for PositionListSerializer."""
        model = Position
        fields = [
            'id', 'title', 'department_name', 'level',
            'salary_range', 'is_active', 'created_at'
        ]


class DepartmentHierarchySerializer(serializers.ModelSerializer):
    """
    Serializer for department hierarchy display.
    
    Used for displaying organizational hierarchy with
    nested sub-departments.
    """
    
    sub_departments = serializers.SerializerMethodField()
    employee_count = serializers.ReadOnlyField()
    
    class Meta:
        """Meta options for DepartmentHierarchySerializer."""
        model = Department
        fields = [
            'id', 'name', 'code', 'manager', 'employee_count',
            'sub_departments', 'is_active'
        ]
    
    def get_sub_departments(self, obj):
        """Get sub-departments recursively."""
        sub_deps = obj.sub_departments.filter(is_active=True)
        return DepartmentHierarchySerializer(sub_deps, many=True).data


class TeamMembershipCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating team memberships.
    
    Handles adding users to teams with validation.
    """
    
    class Meta:
        """Meta options for TeamMembershipCreateSerializer."""
        model = TeamMembership
        fields = ['user', 'team', 'role']
    
    def validate(self, attrs):
        """Validate team membership creation."""
        user = attrs['user']
        team = attrs['team']
        
        # Check if user is already a member
        if TeamMembership.objects.filter(
            user=user, team=team, is_active=True
        ).exists():
            raise serializers.ValidationError(
                'User is already a member of this team.'
            )
        
        # Check if user is in the same department
        if user.department != team.department:
            raise serializers.ValidationError(
                'User must be in the same department as the team.'
            )
        
        return attrs