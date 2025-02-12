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
        
        # Busca anúncios ativos, aprovados e não expirados
        anuncios = Anuncio.objects.filter(
            status='aprovado',
            expira_em__isnull=True  # inclui anúncios sem data de expiração
        ).filter(
            Q(expira_em__gt=timezone.now()) |  # ou com data futura
            Q(expira_em__isnull=True)
        ).select_related(
            'usuario'
        ).prefetch_related(
            'fotos'
        ).order_by('-is_boosted', '-created_at')[:12]
        
        context['anuncios'] = anuncios
        return context

def health_check(request):
    return HttpResponse("OK") 