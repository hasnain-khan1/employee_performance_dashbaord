"""
Views for the org app.

This module contains API views for organizational
structure management including departments, teams, and positions.
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404

from .models import Department, Team, TeamMembership, Position
from .serializers import (
    DepartmentSerializer, DepartmentListSerializer, DepartmentHierarchySerializer,
    TeamSerializer, TeamListSerializer, TeamMembershipSerializer,
    TeamMembershipCreateSerializer, PositionSerializer, PositionListSerializer
)


class DepartmentListView(generics.ListCreateAPIView):
    """
    Department list and creation endpoint.
    
    Provides list of departments with filtering and search,
    and allows creation of new departments.
    """
    
    queryset = Department.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == 'GET':
            return DepartmentListSerializer
        return DepartmentSerializer
    
    def get_queryset(self):
        """Get filtered queryset of departments."""
        queryset = Department.objects.select_related(
            'manager', 'parent_department'
        ).annotate(
            employee_count=Count('employees', filter=Q(employees__status='active'))
        )
        
        # Filter by parent department
        parent = self.request.query_params.get('parent')
        if parent:
            if parent == 'none':
                queryset = queryset.filter(parent_department__isnull=True)
            else:
                queryset = queryset.filter(parent_department_id=parent)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Search by name or code
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )
        
        return queryset.order_by('name')
    
    @extend_schema(
        summary="List Departments",
        description="Get a list of departments with optional filtering.",
        parameters=[
            OpenApiParameter(
                name='parent',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by parent department ID or "none" for root departments'
            ),
            OpenApiParameter(
                name='is_active',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter by active status'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search by department name or code'
            ),
        ],
        responses={
            200: DepartmentListSerializer(many=True),
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get list of departments."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Department",
        description="Create a new department.",
        responses={
            201: DepartmentSerializer,
            400: "Validation error",
            401: "Authentication required"
        }
    )
    def post(self, request, *args, **kwargs):
        """Create a new department."""
        return super().post(request, *args, **kwargs)


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Department detail endpoint.
    
    Provides detailed department information and allows
    updates and deletion.
    """
    
    queryset = Department.objects.select_related('manager', 'parent_department')
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get Department Details",
        description="Retrieve detailed information about a specific department.",
        responses={
            200: DepartmentSerializer,
            404: "Department not found",
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get department details."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update Department",
        description="Update department information.",
        responses={
            200: DepartmentSerializer,
            400: "Validation error",
            404: "Department not found",
            401: "Authentication required"
        }
    )
    def patch(self, request, *args, **kwargs):
        """Update department."""
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete Department",
        description="Delete a department.",
        responses={
            204: "Department deleted successfully",
            404: "Department not found",
            401: "Authentication required"
        }
    )
    def delete(self, request, *args, **kwargs):
        """Delete department."""
        return super().delete(request, *args, **kwargs)


class DepartmentHierarchyView(generics.ListAPIView):
    """
    Department hierarchy endpoint.
    
    Provides hierarchical view of departments with
    nested sub-departments.
    """
    
    serializer_class = DepartmentHierarchySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get root departments for hierarchy display."""
        return Department.objects.filter(
            parent_department__isnull=True,
            is_active=True
        ).select_related('manager')
    
    @extend_schema(
        summary="Get Department Hierarchy",
        description="Get hierarchical view of departments with nested sub-departments.",
        responses={
            200: DepartmentHierarchySerializer(many=True),
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get department hierarchy."""
        return super().get(request, *args, **kwargs)


class TeamListView(generics.ListCreateAPIView):
    """
    Team list and creation endpoint.
    
    Provides list of teams with filtering and search,
    and allows creation of new teams.
    """
    
    queryset = Team.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == 'GET':
            return TeamListSerializer
        return TeamSerializer
    
    def get_queryset(self):
        """Get filtered queryset of teams."""
        queryset = Team.objects.select_related(
            'department', 'team_lead'
        ).annotate(
            member_count=Count('members', filter=Q(teammembership__is_active=True))
        )
        
        # Filter by department
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department_id=department)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Search by name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset.order_by('name')
    
    @extend_schema(
        summary="List Teams",
        description="Get a list of teams with optional filtering.",
        parameters=[
            OpenApiParameter(
                name='department',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by department ID'
            ),
            OpenApiParameter(
                name='is_active',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter by active status'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search by team name'
            ),
        ],
        responses={
            200: TeamListSerializer(many=True),
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get list of teams."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Team",
        description="Create a new team.",
        responses={
            201: TeamSerializer,
            400: "Validation error",
            401: "Authentication required"
        }
    )
    def post(self, request, *args, **kwargs):
        """Create a new team."""
        return super().post(request, *args, **kwargs)


class TeamDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Team detail endpoint.
    
    Provides detailed team information and allows
    updates and deletion.
    """
    
    queryset = Team.objects.select_related('department', 'team_lead')
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get Team Details",
        description="Retrieve detailed information about a specific team.",
        responses={
            200: TeamSerializer,
            404: "Team not found",
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get team details."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update Team",
        description="Update team information.",
        responses={
            200: TeamSerializer,
            400: "Validation error",
            404: "Team not found",
            401: "Authentication required"
        }
    )
    def patch(self, request, *args, **kwargs):
        """Update team."""
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete Team",
        description="Delete a team.",
        responses={
            204: "Team deleted successfully",
            404: "Team not found",
            401: "Authentication required"
        }
    )
    def delete(self, request, *args, **kwargs):
        """Delete team."""
        return super().delete(request, *args, **kwargs)


class TeamMembershipView(generics.ListCreateAPIView):
    """
    Team membership management endpoint.
    
    Handles adding and listing team members.
    """
    
    serializer_class = TeamMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get team memberships for a specific team."""
        team_id = self.kwargs.get('team_id')
        return TeamMembership.objects.filter(
            team_id=team_id,
            is_active=True
        ).select_related('user', 'team')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == 'POST':
            return TeamMembershipCreateSerializer
        return TeamMembershipSerializer
    
    @extend_schema(
        summary="List Team Members",
        description="Get list of team members.",
        responses={
            200: TeamMembershipSerializer(many=True),
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get team members."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Add Team Member",
        description="Add a user to the team.",
        responses={
            201: TeamMembershipSerializer,
            400: "Validation error",
            401: "Authentication required"
        }
    )
    def post(self, request, *args, **kwargs):
        """Add team member."""
        return super().post(request, *args, **kwargs)


class PositionListView(generics.ListCreateAPIView):
    """
    Position list and creation endpoint.
    
    Provides list of positions with filtering and search,
    and allows creation of new positions.
    """
    
    queryset = Position.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == 'GET':
            return PositionListSerializer
        return PositionSerializer
    
    def get_queryset(self):
        """Get filtered queryset of positions."""
        queryset = Position.objects.select_related('department')
        
        # Filter by department
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department_id=department)
        
        # Filter by level
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Search by title
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)
        
        return queryset.order_by('title')
    
    @extend_schema(
        summary="List Positions",
        description="Get a list of positions with optional filtering.",
        parameters=[
            OpenApiParameter(
                name='department',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by department ID'
            ),
            OpenApiParameter(
                name='level',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by position level'
            ),
            OpenApiParameter(
                name='is_active',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter by active status'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search by position title'
            ),
        ],
        responses={
            200: PositionListSerializer(many=True),
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get list of positions."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Position",
        description="Create a new position.",
        responses={
            201: PositionSerializer,
            400: "Validation error",
            401: "Authentication required"
        }
    )
    def post(self, request, *args, **kwargs):
        """Create a new position."""
        return super().post(request, *args, **kwargs)


class PositionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Position detail endpoint.
    
    Provides detailed position information and allows
    updates and deletion.
    """
    
    queryset = Position.objects.select_related('department')
    serializer_class = PositionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get Position Details",
        description="Retrieve detailed information about a specific position.",
        responses={
            200: PositionSerializer,
            404: "Position not found",
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get position details."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update Position",
        description="Update position information.",
        responses={
            200: PositionSerializer,
            400: "Validation error",
            404: "Position not found",
            401: "Authentication required"
        }
    )
    def patch(self, request, *args, **kwargs):
        """Update position."""
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete Position",
        description="Delete a position.",
        responses={
            204: "Position deleted successfully",
            404: "Position not found",
            401: "Authentication required"
        }
    )
    def delete(self, request, *args, **kwargs):
        """Delete position."""
        return super().delete(request, *args, **kwargs)