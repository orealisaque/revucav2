from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.files.storage import default_storage
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings

# Use o cloudinary para manipulação de imagens
import cloudinary
import cloudinary.uploader

# Primeiro definimos Estado e Cidade
class Estado(models.Model):
    nome = models.CharField(max_length=50)
    sigla = models.CharField(max_length=2)

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ['nome']

class Cidade(models.Model):
    nome = models.CharField(max_length=100)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ['nome']

# Depois as outras classes
class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)
    css_class = models.CharField(max_length=100)
    required_reviews = models.IntegerField()
    
    def __str__(self):
        return self.name

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser precisa ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser precisa ter is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('acompanhante', 'Acompanhante'),
        ('cliente', 'Cliente'),
    ]
    
    # Campos básicos
    email = models.EmailField('E-mail', unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='cliente')
    phone = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    
    # Campos de perfil
    foto = models.ImageField(upload_to='users/fotos/', null=True, blank=True)
    whatsapp = models.CharField(
        max_length=20, 
        blank=True,
        help_text="Digite apenas números"
    )
    bio = models.TextField(
        'Biografia',
        max_length=200, 
        blank=True,
        help_text='Máximo de 200 caracteres'
    )
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)
    
    # Redes sociais
    instagram = models.CharField(
        max_length=30,
        blank=True,
        help_text="Digite apenas seu nome de usuário, sem @ (opcional)"
    )
    
    # Configurações
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    PLANO_CHOICES = [
        ('free', 'Gratuito'),
        ('vip', 'VIP'),
    ]
    
    plano = models.CharField(max_length=10, choices=PLANO_CHOICES, default='free')
    plano_expira_em = models.DateTimeField(null=True, blank=True)
    is_vip = models.BooleanField(
        'VIP',
        default=False,
        help_text='Indica se o usuário tem plano VIP ativo'
    )
    
    total_boosts = models.IntegerField(default=0)
    
    username = models.CharField('Username', max_length=150, unique=True, blank=True, null=True)
    
    objects = CustomUserManager()
    
    @property
    def plano_atual(self):
        """Retorna as informações do plano atual baseado no status VIP"""
        if self.is_vip:
            return {
                'nome': 'VIP',
                'tipo': 'premium',
                'max_anuncios': 2,
                'max_fotos': 10,
                'max_videos': 4,
                'expira_em': self.plano_expira_em
            }
            
        return {
            'nome': 'Gratuito',
            'tipo': 'basic',
            'max_anuncios': 1,
            'max_fotos': 5,
            'max_videos': 1,
            'expira_em': None
        }
    
    @property
    def max_anuncios(self):
        return self.plano_atual['max_anuncios']
        
    @property
    def max_fotos(self):
        return self.plano_atual['max_fotos']
        
    @property
    def max_videos(self):
        return self.plano_atual['max_videos']
    
    @property
    def total_boosts(self):
        """Retorna o total de boosts usados"""
        from ads.models import Anuncio
        return Anuncio.objects.filter(usuario=self, is_boosted=True).count()
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        swappable = 'AUTH_USER_MODEL'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['user_type']),
            models.Index(fields=['cidade']),
            models.Index(fields=['estado']),
            models.Index(fields=['plano']),
            models.Index(fields=['is_vip']),
        ]

    def __str__(self):
        return self.email

    def get_progress(self):
        """Retorna o progresso do perfil em porcentagem"""
        items = [
            {'label': 'Foto do Perfil', 'complete': bool(self.foto), 'weight': 20},
            {'label': 'WhatsApp', 'complete': bool(self.whatsapp), 'weight': 20},
            {'label': 'Bio', 'complete': bool(self.bio), 'weight': 20},
            {'label': 'Localização', 'complete': bool(self.cidade), 'weight': 20},
            {'label': 'Nome Completo', 'complete': bool(self.get_full_name()), 'weight': 20}
        ]
        
        total_weight = sum(item['weight'] for item in items)
        completed_weight = sum(item['weight'] for item in items if item['complete'])
        
        for item in items:
            item['percentage'] = (item['weight'] / total_weight) * 100 if item['complete'] else 0
            
        return items
    
    def get_total_progress(self):
        """Retorna o progresso total em porcentagem"""
        progress = self.get_progress()
        total_weight = sum(item['weight'] for item in progress)
        completed_weight = sum(item['weight'] for item in progress if item['complete'])
        
        return (completed_weight / total_weight) * 100
    
    def get_next_badge(self):
        review_count = getattr(self, 'reviews_received', None)
        if not review_count:
            return Badge.objects.filter(required_reviews__gt=0).order_by('required_reviews').first()
            
        review_count = review_count.count()
        return Badge.objects.filter(
            required_reviews__gt=review_count
        ).order_by('required_reviews').first()
    
    def get_badge_progress(self):
        next_badge = self.get_next_badge()
        if not next_badge:
            return 100
            
        review_count = getattr(self, 'reviews_received', None)
        if not review_count:
            return 0
            
        review_count = review_count.count()
        previous_badge = Badge.objects.filter(
            required_reviews__lt=next_badge.required_reviews
        ).order_by('-required_reviews').first()
        
        previous_reviews = previous_badge.required_reviews if previous_badge else 0
        total_needed = next_badge.required_reviews - previous_reviews
        current_progress = review_count - previous_reviews
        
        return (current_progress / total_needed) * 100

    def calculate_vip_status(self):
        """Calcula se o usuário tem status VIP baseado no plano e data de expiração"""
        return (
            self.plano == 'vip' and 
            self.plano_expira_em and 
            self.plano_expira_em > timezone.now()
        )
    
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
            
        # Sempre atualiza o status VIP antes de salvar
        self.is_vip = bool(
            self.plano == 'vip' and 
            self.plano_expira_em and 
            self.plano_expira_em > timezone.now()
        )
            
        # Otimiza a foto do perfil antes de salvar
        if self.foto and hasattr(self.foto, 'file'):
            img = Image.open(self.foto)
            
            # Converte para RGB se necessário
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Redimensiona mantendo proporção
            max_size = (800, 800)
            img.thumbnail(max_size, Image.LANCZOS)
            
            # Salva com compressão otimizada
            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            
            # Substitui o arquivo original
            self.foto.save(
                self.foto.name,
                ContentFile(output.getvalue()),
                save=False
            )
            
        super().save(*args, **kwargs)

    def get_missing_fields(self):
        """Retorna uma lista de campos que faltam ser preenchidos"""
        missing = []
        
        if not self.first_name or not self.last_name:
            missing.append('Nome completo')
        
        if not self.foto:
            missing.append('Foto do perfil')
            
        if not self.whatsapp:
            missing.append('WhatsApp')
            
        if not self.bio:
            missing.append('Biografia')
            
        if not self.cidade:
            missing.append('Localização (Cidade)')
            
        if not self.estado:
            missing.append('Localização (Estado)')
            
        return missing

    def is_profile_complete(self):
        """Verifica se o perfil está completo para publicação de anúncios"""
        return len(self.get_missing_fields()) == 0

    def get_profile_completion_message(self):
        """Retorna uma mensagem personalizada sobre o status do perfil"""
        missing_fields = self.get_missing_fields()
        
        if not missing_fields:
            return {
                'complete': True,
                'message': 'Seu perfil está completo! Você já pode publicar anúncios.',
                'missing_fields': []
            }
        
        return {
            'complete': False,
            'message': 'Complete seu perfil para poder publicar anúncios. Precisamos de:',
            'missing_fields': missing_fields
        }
    
    def get_total_views(self):
        """Retorna o total de visualizações de todos os anúncios"""
        from ads.models import Anuncio
        return Anuncio.objects.filter(usuario=self).aggregate(
            total_views=models.Sum('views')
        )['total_views'] or 0

    def debug_plano(self):
        """Método para debug das informações do plano"""
        return {
            'plano': self.plano,
            'expira_em': self.plano_expira_em,
            'is_vip': self.is_vip,
            'now': timezone.now(),
            'max_fotos': self.max_fotos,
            'max_videos': self.max_videos
        }

class AcompanhanteProfile(models.Model):
    user = models.OneToOneField('users.CustomUser', on_delete=models.CASCADE)
    nome_completo = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='fotos/', null=True, blank=True)
    whatsapp = models.CharField(max_length=20, null=True, blank=True)
    instagram = models.CharField(max_length=50, null=True, blank=True)
    biografia = models.TextField(null=True, blank=True)
    estado = models.ForeignKey(Estado, on_delete=models.SET_NULL, null=True, blank=True)
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Perfil de {self.user.email}"

    class Meta:
        verbose_name = 'Perfil de Acompanhante'
        verbose_name_plural = 'Perfis de Acompanhantes'
        indexes = [
            models.Index(fields=['user']),
        ]

class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 estrela'),
        (2, '2 estrelas'),
        (3, '3 estrelas'),
        (4, '4 estrelas'),
        (5, '5 estrelas'),
    ]
    
    author = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='reviews_given'
    )
    recipient = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='reviews_received'
    )
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        ordering = ['-created_at']
        
    def __str__(self):
        return f'Avaliação de {self.author} para {self.recipient}' 

    # ... (resto do código permanece igual) 