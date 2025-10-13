"""
URL configuration for the workflows app.
"""

from django.urls import path
from . import views

app_name = 'workflows'

urlpatterns = [
    # Workflow Steps
    path('steps/', views.WorkflowStepListView.as_view(), name='workflow-step-list'),
    path('steps/<int:pk>/', views.WorkflowStepDetailView.as_view(), name='workflow-step-detail'),
    path('steps/<int:pk>/update-status/', views.update_workflow_status, name='workflow-step-update-status'),
    
    # Notifications
    path('notifications/', views.WorkflowNotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/', views.WorkflowNotificationDetailView.as_view(), name='notification-detail'),
    path('notifications/<int:pk>/mark-read/', views.mark_notification_read, name='notification-mark-read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='notification-mark-all-read'),
    
    # Audit Logs
    path('audit-logs/', views.AuditLogListView.as_view(), name='audit-log-list'),
    path('audit-logs/<int:pk>/', views.AuditLogDetailView.as_view(), name='audit-log-detail'),
]

