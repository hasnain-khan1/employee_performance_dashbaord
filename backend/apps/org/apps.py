from django.apps import AppConfig


class OrgConfig(AppConfig):
    """Configuration for the org app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.org'
    verbose_name = 'Organization'