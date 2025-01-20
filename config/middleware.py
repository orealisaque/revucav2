import logging
from django.contrib import messages
from django.urls import reverse
from django.urls import reverse_lazy

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            logger.error(f"Erro não tratado: {str(e)}")
            messages.error(request, "Ocorreu um erro inesperado")
            return reverse_lazy('core:home') 