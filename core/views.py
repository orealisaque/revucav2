from django.shortcuts import render
from django.views.generic import TemplateView
from ads.models import Anuncio, Categoria
from billing.models import Plan
from django.core.serializers import serialize
import json
import requests
from django.db.models import Count, Q
from django.utils import timezone
from django.http import HttpResponse

class HomeView(TemplateView):
    template_name = 'core/home.html'
    
    def get_user_location(self):
        try:
            # Usar API de geolocalização por IP
            response = requests.get('https://ipapi.co/json/')
            data = response.json()
            return {
                'latitude': float(data['latitude']),
                'longitude': float(data['longitude'])
            }
        except:
            return None
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['anuncios'] = Anuncio.objects.filter(
            status='aprovado'
        ).select_related(
            'usuario',
            'usuario__cidade_ref',
            'usuario__estado_ref'
        ).order_by('-created_at')[:6]
        return context

def health_check(request):
    return HttpResponse("OK") 