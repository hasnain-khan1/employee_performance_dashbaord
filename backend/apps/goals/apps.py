from django.apps import AppConfig


class GoalsConfig(AppConfig):
    """Configuration for the goals app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.goals'
    verbose_name = 'Goals Management'