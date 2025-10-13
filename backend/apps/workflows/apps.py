"""
App configuration for workflows.
"""

from django.apps import AppConfig


class WorkflowsConfig(AppConfig):
    """Configuration for the workflows app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.workflows'
    verbose_name = 'Workflow Management'

