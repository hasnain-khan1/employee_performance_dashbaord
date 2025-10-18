from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import redis
import logging

logger = logging.getLogger(__name__)

def health_check(request):
    """
    Comprehensive health check endpoint for the EPMS application.
    Checks database, cache, and basic application functionality.
    """
    health_status = {
        'status': 'healthy',
        'checks': {},
        'timestamp': None
    }
    
    from django.utils import timezone
    health_status['timestamp'] = timezone.now().isoformat()
    
    # Check database connectivity
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_status['checks']['database'] = {
                'status': 'healthy',
                'message': 'Database connection successful'
            }
    except Exception as e:
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}'
        }
        health_status['status'] = 'unhealthy'
    
    # Check Redis cache connectivity
    try:
        cache.set('health_check', 'ok', 10)
        cache_result = cache.get('health_check')
        if cache_result == 'ok':
            health_status['checks']['cache'] = {
                'status': 'healthy',
                'message': 'Cache connection successful'
            }
        else:
            health_status['checks']['cache'] = {
                'status': 'unhealthy',
                'message': 'Cache read/write test failed'
            }
            health_status['status'] = 'unhealthy'
    except Exception as e:
        health_status['checks']['cache'] = {
            'status': 'unhealthy',
            'message': f'Cache connection failed: {str(e)}'
        }
        health_status['status'] = 'unhealthy'
    
    # Check application settings
    try:
        health_status['checks']['settings'] = {
            'status': 'healthy',
            'message': 'Application settings loaded',
            'debug': settings.DEBUG,
            'database_engine': settings.DATABASES['default']['ENGINE']
        }
    except Exception as e:
        health_status['checks']['settings'] = {
            'status': 'unhealthy',
            'message': f'Settings check failed: {str(e)}'
        }
        health_status['status'] = 'unhealthy'
    
    # Determine HTTP status code
    http_status = 200 if health_status['status'] == 'healthy' else 503
    
    return JsonResponse(health_status, status=http_status)

def readiness_check(request):
    """
    Readiness check for Kubernetes/Docker orchestration.
    Simpler check for load balancer health checks.
    """
    try:
        # Quick database check
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Quick cache check
        cache.set('readiness_check', 'ok', 5)
        
        return JsonResponse({
            'status': 'ready',
            'message': 'Application is ready to serve requests'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'not_ready',
            'message': f'Application not ready: {str(e)}'
        }, status=503)

def liveness_check(request):
    """
    Liveness check for Kubernetes/Docker orchestration.
    Basic check to ensure the application is running.
    """
    return JsonResponse({
        'status': 'alive',
        'message': 'Application is running'
    })
