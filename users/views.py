from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView, TemplateView, DetailView
from django.urls import reverse_lazy
from .models import CustomUser, AcompanhanteProfile, Badge, Cidade, Estado
from .forms import CustomSignupForm, ProfileEditForm
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

@method_decorator(cache_page(60 * 5), name='dispatch')
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'users/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            anuncios = Anuncio.objects.filter(usuario=user)
            
            context.update({
                'user': user,
                'plano_info': user.plano_atual,
                'profile_progress': user.get_progress(),
                'total_progress': user.get_total_progress(),
                'next_badge': user.get_next_badge(),
                'anuncios_stats': {
                    'total': anuncios.count(),
                    'aprovado': anuncios.filter(status='aprovado').count(),
                },
                'total_views': user.get_total_views(),
                'profile_complete': user.is_profile_complete(),
            })
            
        except Exception as e:
            print(f"Erro no dashboard: {str(e)}")
            context.update({
                'anuncios_stats': {
                    'total': 0,
                    'aprovado': 0,
                },
                'total_views': 0,
            })
        
        return context

@method_decorator(csrf_protect, name='dispatch')
class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = AcompanhanteProfile
    form_class = ProfileEditForm
    template_name = 'users/profile_edit.html'
    success_url = '/users/dashboard/'
    
    def get_object(self, queryset=None):
        # Retorna o perfil do usuário atual ou cria um novo
        profile, created = AcompanhanteProfile.objects.get_or_create(user=self.request.user)
        return profile
    
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

@login_required
def profile_update(request):
    try:
        profile = request.user.acompanhanteprofile
    except AcompanhanteProfile.DoesNotExist:
        profile = AcompanhanteProfile.objects.create(usuario=request.user)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('users:dashboard')
    else:
        form = ProfileEditForm(instance=profile)
    
    return render(request, 'users/profile_update.html', {
        'form': form
    }) 