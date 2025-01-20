from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from .models import Subscription
from django.conf import settings

class SubscriptionRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.user_type == 'anunciante':
            if not hasattr(request.user, 'subscription'):
                if request.path.startswith('/ads/create'):
                    messages.warning(request, 'Você precisa de uma assinatura ativa para criar anúncios.')
                    return redirect('billing:plan_list')
        
        response = self.get_response(request)
        return response 

class StripeContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            request.stripe_public_key = settings.STRIPE_PUBLIC_KEY
        return self.get_response(request) 