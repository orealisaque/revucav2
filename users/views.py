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
import logging

logger = logging.getLogger(__name__)

@login_required
def profile(request):
    anuncios = request.user.anuncio_set.all().order_by('-created_at')
    return render(request, 'users/profile.html', {'anuncios': anuncios})

@method_decorator(cache_page(60 * 5), name='dispatch')
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'users/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # Usar select_related para evitar N+1 queries
            user = CustomUser.objects.select_related(
                'acompanhanteprofile'
            ).get(id=self.request.user.id)
            
            # Usar prefetch_related para relacionamentos many-to-many
            anuncios = Anuncio.objects.filter(
                usuario=user
            ).select_related('cidade', 'estado')
            
            context.update({
                'user': user,
                'anuncios_count': anuncios.count(),  # Mais eficiente que len(anuncios)
            })
        except Exception as e:
            logger.error(f"Erro no dashboard: {str(e)}")
            messages.error(self.request, "Erro ao carregar dashboard")
            context.update({'error': True})
        return context

@method_decorator(csrf_protect, name='dispatch')
class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = AcompanhanteProfile
    form_class = ProfileEditForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:dashboard')

    def get_object(self, queryset=None):
        try:
            return AcompanhanteProfile.objects.select_related('user').get(
                user=self.request.user
            )
        except AcompanhanteProfile.DoesNotExist:
            return AcompanhanteProfile.objects.create(
                user=self.request.user,
                nome_completo=self.request.user.get_full_name() or self.request.user.email
            )
    
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
def get_cidades(request, estado_id):
    # Usar .exists() primeiro para evitar queries desnecessárias
    if not Estado.objects.filter(id=estado_id).exists():
        return JsonResponse({'error': 'Estado não encontrado'}, status=404)
        
    cidades = Cidade.objects.filter(estado_id=estado_id).values('id', 'nome')
    return JsonResponse(list(cidades), safe=False) 

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