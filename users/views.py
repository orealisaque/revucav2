from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView, TemplateView, DetailView
from django.urls import reverse_lazy
from .models import CustomUser, AcompanhanteProfile, Badge, Cidade, Estado
from .forms import CustomSignupForm, ProfileUpdateForm, UserProfileForm, ProfileEditForm
from ads.models import Anuncio, AnuncioFoto
from datetime import date
from billing.models import Subscription
from django.db.models import Count, Sum, Q
from django.conf import settings
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.http import JsonResponse
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import logout
from .services import IBGEService
from django.views.decorators.http import require_http_methods

@login_required
def profile(request):
    anuncios = request.user.anuncio_set.all().order_by('-created_at')
    return render(request, 'users/profile.html', {'anuncios': anuncios})

@method_decorator(cache_page(60 * 5), name='dispatch')  # Cache por 5 minutos
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'users/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stripe_key = settings.STRIPE_PUBLIC_KEY
        print(f"Stripe Public Key: {stripe_key}")  # Para debug
        context['stripe_public_key'] = stripe_key
        user = self.request.user
        
        # Cache key único para o usuário
        cache_key = f'dashboard_data_{user.id}'
        
        # Tenta pegar dados do cache
        cached_data = cache.get(cache_key)
        if cached_data:
            context.update(cached_data)
            return context
            
        try:
            # Otimiza queries usando select_related e prefetch_related
            anuncios = (Anuncio.objects
                       .filter(usuario=user)
                       .select_related('categoria')
                       .prefetch_related(
                           Prefetch('fotos', queryset=AnuncioFoto.objects.order_by('ordem')),
                           'videos'
                       ))
            
            # Agrupa todas as contagens em uma única query
            anuncios_stats = anuncios.aggregate(
                total=Count('id'),
                pendente=Count('id', filter=Q(status='pendente')),
                aprovado=Count('id', filter=Q(status='aprovado')),
                rejeitado=Count('id', filter=Q(status='rejeitado')),
                total_views=Sum('views')
            )
            
            # Pega apenas os últimos 5 anúncios
            ultimos_anuncios = anuncios.order_by('-created_at')[:5]
            
            # Verifica se é usuário VIP
            is_vip = user.subscription_set.filter(
                plan__name='VIP',
                is_active=True,
                end_date__gt=timezone.now()
            ).exists()
            
            if is_vip:
                # Últimos 7 dias
                end_date = timezone.now()
                start_date = end_date - timedelta(days=7)
                
                # Busca visualizações agrupadas por dia
                views_data = AnuncioView.objects.filter(
                    anuncio__usuario=user,
                    data__range=(start_date, end_date)
                ).annotate(
                    date=TruncDate('data')
                ).values('date').annotate(
                    count=Count('id')
                ).order_by('date')
                
                # Formata dados para o gráfico
                dates = []
                counts = []
                
                current = start_date.date()
                while current <= end_date.date():
                    dates.append(current.strftime('%d/%m'))
                    view_count = next(
                        (item['count'] for item in views_data if item['date'] == current),
                        0
                    )
                    counts.append(view_count)
                    current += timedelta(days=1)
                
                context['views_chart_data'] = {
                    'labels': dates,
                    'data': counts
                }
            
            data = {
                'plano_info': user.plano_atual,
                'profile_progress': user.get_progress(),
                'total_progress': user.get_total_progress(),
                'next_badge': user.get_next_badge(),
                'badge_progress': user.get_badge_progress(),
                'anuncios_stats': anuncios_stats,
                'ultimos_anuncios': ultimos_anuncios,
                'review_count': user.reviews_received.count(),
                'total_views': anuncios_stats['total_views'] or 0,
                'profile_complete': user.is_profile_complete(),
            }
            
            # Salva no cache
            cache.set(cache_key, data, timeout=60 * 5)
            
            context.update(data)
            
        except Exception as e:
            print(f"Erro no dashboard: {str(e)}")
            context.update({
                'plano_info': user.plano_atual,
                'profile_progress': [],
                'total_progress': 0,
                'next_badge': None,
                'badge_progress': 0,
                'anuncios_stats': {
                    'total': 0,
                    'pendente': 0,
                    'aprovado': 0,
                    'rejeitado': 0
                },
                'ultimos_anuncios': [],
                'review_count': 0,
                'total_views': 0,
                'profile_complete': False,
            })
        
        return context

@method_decorator(csrf_protect, name='dispatch')
class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileEditForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Perfil atualizado com sucesso!')
        return response

class ProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'
    
    def get_object(self):
        return self.request.user
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['anuncios'] = Anuncio.objects.filter(
            usuario=self.request.user
        ).order_by('-created_at')
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        return context 

def profile_edit(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('users:dashboard')
    else:
        form = UserEditForm(instance=request.user)
    
    estados = Estado.objects.all()
    return render(request, 'users/profile_edit.html', {
        'form': form,
        'estados': estados
    }) 

@cache_page(60 * 60 * 24)  # Cache por 24 horas
def get_cidades(request):
    estado_id = request.GET.get('estado_id')
    cache_key = f'cidades_estado_{estado_id}'
    
    cidades = cache.get(cache_key)
    if not cidades:
        cidades = list(Cidade.objects
                      .filter(estado_id=estado_id)
                      .values('id', 'nome')
                      .order_by('nome'))
        cache.set(cache_key, cidades, timeout=60 * 60 * 24)
    
    return JsonResponse(cidades, safe=False) 

def custom_logout(request):
    logout(request)
    messages.success(request, 'Você saiu com sucesso.')
    return redirect('account_login') 

@require_http_methods(["GET"])
def get_estados(request):
    estados = IBGEService.get_estados()
    return JsonResponse(estados, safe=False)

@require_http_methods(["GET"])
def get_cidades(request):
    uf = request.GET.get('uf')
    if not uf:
        return JsonResponse({'error': 'UF é obrigatório'}, status=400)
        
    cidades = IBGEService.get_cidades(uf)
    return JsonResponse(cidades, safe=False) 