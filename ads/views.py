from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse
from .models import Anuncio, AnuncioFoto, AnuncioVideo, Categoria, AnuncioView
from .forms import AnuncioForm
from django.db.models import F, Case, When, Value, BooleanField
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib import messages

class AnuncioListView(LoginRequiredMixin, ListView):
    model = Anuncio
    template_name = 'ads/anuncio_list.html'
    context_object_name = 'anuncios'
    paginate_by = 12  # Paginação para reduzir carga
    
    def get_queryset(self):
        return (
            Anuncio.objects
            .filter(status='aprovado')
            .select_related('usuario', 'categoria')  # Reduz queries
            .prefetch_related('fotos')  # Carrega fotos em uma única query
            .annotate(
                is_vip=Case(
                    When(
                        usuario__plano='vip',
                        usuario__plano_expira_em__gt=timezone.now(),
                        then=Value(True)
                    ),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            )
            .order_by(
                '-is_boosted',  # Boosted primeiro
                '-is_vip',      # VIP segundo
                '-created_at'   # Mais recentes depois
            )
        )

class AnuncioCreateView(LoginRequiredMixin, CreateView):
    model = Anuncio
    form_class = AnuncioForm
    template_name = 'ads/anuncio_form.html'
    success_url = reverse_lazy('users:dashboard')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_profile_complete():
            messages.error(
                request,
                'Complete seu perfil antes de criar um anúncio. '
                'Precisamos de: foto do perfil, WhatsApp, bio, cidade e nome completo.'
            )
            return redirect('users:profile_edit')
        
        user = request.user
        anuncios_ativos = Anuncio.objects.filter(
            usuario=user,
            status__in=['aprovado', 'pendente']
        ).count()
        
        if anuncios_ativos >= user.max_anuncios:
            messages.error(
                request,
                f'Você atingiu o limite de {user.max_anuncios} anúncios ativos. '
                'Faça upgrade para o plano VIP para publicar mais anúncios.'
            )
            return redirect('users:dashboard')
            
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            self.object = form.save(commit=False)
            self.object.usuario = self.request.user
            self.object.save()
            
            # Processa as fotos
            for foto in self.request.FILES.getlist('fotos'):
                AnuncioFoto.objects.create(
                    anuncio=self.object,
                    imagem=foto,
                    ordem=AnuncioFoto.objects.filter(anuncio=self.object).count(),
                    is_capa=AnuncioFoto.objects.filter(anuncio=self.object).count() == 0
                )
            
            # Processa o vídeo
            video = self.request.FILES.get('video')
            if video:
                AnuncioVideo.objects.create(
                    anuncio=self.object,
                    video=video
                )
            
            # Valida os limites após criar as fotos/vídeos
            self.object.validate_limits()
            
            return HttpResponseRedirect(self.get_success_url())
            
        except ValidationError as e:
            # Se houver erro de validação, remove o anúncio e suas fotos/vídeos
            if self.object.pk:
                self.object.delete()
            form.add_error(None, e)
            return self.form_invalid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

class AnuncioUpdateView(LoginRequiredMixin, UpdateView):
    model = Anuncio
    form_class = AnuncioForm
    template_name = 'ads/anuncio_form.html'
    success_url = reverse_lazy('users:dashboard')
    
    def get_queryset(self):
        return Anuncio.objects.filter(usuario=self.request.user)
        
    def form_valid(self, form):
        anuncio = form.save(commit=False)
        anuncio.status = 'pendente'  # Volta para análise após edição
        return super().form_valid(form)

class AnuncioDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Anuncio
    success_url = reverse_lazy('users:dashboard')
    template_name = 'ads/anuncio_confirm_delete.html'
    
    def test_func(self):
        anuncio = self.get_object()
        return self.request.user == anuncio.usuario

class AnuncioDetailView(DetailView):
    model = Anuncio
    template_name = 'ads/anuncio_detail.html'
    context_object_name = 'anuncio'

    def get_queryset(self):
        return super().get_queryset().filter(status='aprovado') 

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        
        # Registra a visualização
        ip = request.META.get('REMOTE_ADDR')
        anuncio = self.object
        
        # Verifica se já visualizou nas últimas 24h
        ultima_view = AnuncioView.objects.filter(
            anuncio=anuncio,
            ip=ip,
            data__gte=timezone.now() - timezone.timedelta(days=1)
        ).first()
        
        if not ultima_view:
            AnuncioView.objects.create(anuncio=anuncio, ip=ip)
            anuncio.views = F('views') + 1
            anuncio.save()
        
        return response

def anuncio_modal(request, pk):
    try:
        anuncio = get_object_or_404(Anuncio, pk=pk)
        data = {
            'titulo': anuncio.titulo,
            'descricao': anuncio.descricao,
            'cidade': anuncio.cidade,
            'whatsapp': anuncio.usuario.whatsapp if anuncio.usuario.whatsapp else '',
            'fotos': [{'url': foto.imagem.url} for foto in anuncio.fotos.all()],
            'videos': [{
                'url': video.video.url,
                'thumbnail': video.thumbnail.url if video.thumbnail else None
            } for video in anuncio.videos.all()],
            'preco': float(anuncio.preco),
            'categoria': anuncio.categoria.nome if anuncio.categoria else '',
            'status': anuncio.get_status_display(),
            'created_at': anuncio.created_at.strftime('%d/%m/%Y')
        }
        return JsonResponse(data)
    except Exception as e:
        print(f"Erro ao carregar anúncio: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400) 

def anuncios_ativos(request):
    try:
        anuncios = Anuncio.objects.filter(
            status='aprovado'
        ).select_related(
            'usuario', 
            'categoria'
        ).prefetch_related(
            'fotos'
        ).order_by('-created_at')[:12]
        
        data = []
        for anuncio in anuncios:
            fotos = [{'url': foto.imagem.url} for foto in anuncio.fotos.all()]
            
            anuncio_data = {
                'id': anuncio.id,
                'titulo': anuncio.titulo,
                'descricao': anuncio.descricao,
                'cidade': anuncio.cidade,
                'preco': float(anuncio.preco),
                'fotos': fotos,
                'created_at': anuncio.created_at.strftime('%d/%m/%Y'),
                'categoria': anuncio.categoria.nome if anuncio.categoria else '',
                'usuario': {
                    'nome': anuncio.usuario.get_full_name() or anuncio.usuario.email,
                    'foto': anuncio.usuario.foto.url if anuncio.usuario.foto else None
                }
            }
            
            # Adiciona vídeo se existir
            try:
                video = anuncio.videos.first()
                if video:
                    anuncio_data['video'] = video.video.url
            except:
                anuncio_data['video'] = None
                
            data.append(anuncio_data)
        
        return JsonResponse(data, safe=False)
    except Exception as e:
        import traceback
        print(f"Erro ao buscar anúncios ativos: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=400)

def anuncios_por_categoria(request, categoria):
    try:
        anuncios = Anuncio.objects.filter(
            status='aprovado',
            categoria__nome__iexact=categoria
        ).select_related(
            'usuario', 
            'categoria'
        ).prefetch_related(
            'fotos', 
            'video'
        ).order_by('-created_at')
        
        data = [{
            'id': anuncio.id,
            'titulo': anuncio.titulo,
            'descricao': anuncio.descricao,
            'cidade': anuncio.cidade,
            'preco': float(anuncio.preco),
            'fotos': [{'url': foto.imagem.url} for foto in anuncio.fotos.all()],
            'video': anuncio.video.video.url if hasattr(anuncio, 'video') and anuncio.video else None,
            'created_at': anuncio.created_at.strftime('%d/%m/%Y'),
            'categoria': anuncio.categoria.nome if anuncio.categoria else '',
            'usuario': {
                'nome': anuncio.usuario.get_full_name() or anuncio.usuario.email,
                'foto': anuncio.usuario.foto.url if anuncio.usuario.foto else None
            }
        } for anuncio in anuncios]
        
        if not anuncios:
            return JsonResponse({'error': 'Nenhum anúncio encontrado nesta categoria'}, status=404)
        
        return JsonResponse(data, safe=False)
    except Exception as e:
        print(f"Erro ao buscar anúncios: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400) 

def categoria_list(request, slug):
    categoria = get_object_or_404(Categoria, slug=slug)
    anuncios = Anuncio.objects.filter(
        categoria=categoria,
        status='aprovado'
    ).select_related(
        'usuario',
        'categoria'
    ).prefetch_related(
        'fotos',
        'videos'
    ).order_by('-created_at')
    
    return render(request, 'ads/categoria_list.html', {
        'categoria': categoria,
        'anuncios': anuncios
    }) 

def anuncio_api_detail(request, pk):
    try:
        anuncio = Anuncio.objects.get(pk=pk)
        data = {
            'id': anuncio.id,
            'titulo': anuncio.titulo,
            'descricao': anuncio.descricao,
            'preco_formatado': anuncio.get_preco_formatado(),
            'views': anuncio.views,
            'primeira_foto': anuncio.get_primeira_foto().imagem.url if anuncio.get_primeira_foto() else None,
            'cidade': anuncio.cidade,
            'categoria': anuncio.categoria.nome if anuncio.categoria else None,
            'whatsapp': anuncio.usuario.whatsapp.replace('+', '').replace(' ', '') if anuncio.usuario.whatsapp else '',
        }
        return JsonResponse(data)
    except Anuncio.DoesNotExist:
        return JsonResponse({'error': 'Anúncio não encontrado'}, status=404) 