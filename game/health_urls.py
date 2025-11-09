from django.urls import path
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'Zugu Ludo Backend'
    })

urlpatterns = [
    path('', health_check, name='health-check'),
]
