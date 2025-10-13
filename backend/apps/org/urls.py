"""
URL configuration for the org app.

This module defines the URL patterns for organizational
structure management endpoints.
"""

from django.urls import path, include
from . import views

app_name = 'org'

urlpatterns = [
    # Department endpoints
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/hierarchy/', views.DepartmentHierarchyView.as_view(), name='department_hierarchy'),
    path('departments/<int:pk>/', views.DepartmentDetailView.as_view(), name='department_detail'),
    
    # Team endpoints
    path('teams/', views.TeamListView.as_view(), name='team_list'),
    path('teams/<int:pk>/', views.TeamDetailView.as_view(), name='team_detail'),
    path('teams/<int:team_id>/members/', views.TeamMembershipView.as_view(), name='team_members'),
    
    # Position endpoints
    path('positions/', views.PositionListView.as_view(), name='position_list'),
    path('positions/<int:pk>/', views.PositionDetailView.as_view(), name='position_detail'),
]