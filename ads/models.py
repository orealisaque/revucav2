from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.files import File
import subprocess
import os
from PIL import Image
import tempfile
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    imagem = models.ImageField(
        upload_to='categorias/',
        null=True,
        blank=True,
        help_text="Imagem de capa da categoria"
    )
    icone = models.CharField(
        max_length=50,
        blank=True,
        help_text="Classe do ícone FontAwesome (ex: fas fa-users)"
    )
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)
    
    def get_imagem_url(self):
        if self.imagem:
            return self.imagem.url
        return f'/static/images/categorias/{self.slug}.jpg'
    
    def get_icone(self):
        if self.icone:
            return self.icone
        icones = {
            'acompanhante': 'fas fa-users',
            'videochamada': 'fas fa-video'
        }
        return icones.get(self.slug, 'fas fa-tag')
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

class Anuncio(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
    )
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    cidade = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_boosted = models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    boost_expira_em = models.DateTimeField(null=True, blank=True)
    boost_views_antes = models.IntegerField(default=0)
    expira_em = models.DateTimeField(null=True, blank=True)
    
    @property
    def boost_impacto(self):
        """Retorna o impacto percentual do boost nas visualizações"""
        if not self.is_boosted or not self.boost_views_antes:
            return 0
        views_durante_boost = self.views - self.boost_views_antes
        if views_durante_boost <= 0:
            return 0
        return int((views_durante_boost / self.boost_views_antes) * 100)

    def get_primeira_foto(self):
        return self.fotos.filter(is_capa=True).first() or self.fotos.first()

    def __str__(self):
        return self.titulo

    def clean(self):
        super().clean()

    def validate_limits(self):
        """Valida os limites de fotos e vídeos após o salvamento"""
        fotos_count = self.fotos.count()
        videos_count = self.videos.count()
        
        if fotos_count > self.usuario.max_fotos:
            raise ValidationError(f'Você pode ter no máximo {self.usuario.max_fotos} fotos no seu plano atual.')
            
        if videos_count > self.usuario.max_videos:
            raise ValidationError(f'Você pode ter no máximo {self.usuario.max_videos} vídeos no seu plano atual.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def get_preco_formatado(self):
        try:
            return f"R$ {self.preco:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
        except:
            return "R$ 0,00"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['is_boosted']),
            models.Index(fields=['categoria']),
        ]

class AnuncioFoto(models.Model):
    anuncio = models.ForeignKey(
        Anuncio, 
        related_name='fotos', 
        on_delete=models.CASCADE
    )
    imagem = models.ImageField(upload_to='anuncios/fotos/')
    ordem = models.IntegerField(default=0)
    is_capa = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordem']

class AnuncioVideo(models.Model):
    anuncio = models.ForeignKey(
        Anuncio, 
        related_name='videos', 
        on_delete=models.CASCADE
    )
    video = models.FileField(upload_to='anuncios/videos/')
    thumbnail = models.ImageField(
        upload_to='anuncios/thumbnails/', 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def generate_thumbnail(self):
        if not self.video:
            return
            
        temp_dir = tempfile.mkdtemp()
        temp_thumb = os.path.join(temp_dir, 'thumb.jpg')
        
        try:
            # Verifica se ffmpeg está instalado
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            
            # Extrai o primeiro frame do vídeo
            cmd = [
                'ffmpeg', '-i', self.video.path,
                '-ss', '00:00:01',
                '-vframes', '1',
                '-vf', 'scale=640:360',  # Redimensiona para 640x360
                '-y',  # Sobrescreve arquivo existente
                temp_thumb
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Otimiza e salva o thumbnail
            if os.path.exists(temp_thumb):
                with open(temp_thumb, 'rb') as f:
                    self.thumbnail.save(
                        f'thumb_{os.path.basename(self.video.name)}.jpg',
                        File(f),
                        save=True
                    )
        except subprocess.CalledProcessError as e:
            print(f"Erro ao gerar thumbnail: {e.stderr.decode()}")
        except Exception as e:
            print(f"Erro ao processar thumbnail: {str(e)}")
        finally:
            # Limpa arquivos temporários
            try:
                if os.path.exists(temp_thumb):
                    os.remove(temp_thumb)
                os.rmdir(temp_dir)
            except:
                pass
    
    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)
        if is_new and not self.thumbnail:
            self.generate_thumbnail() 

class AnuncioView(models.Model):
    anuncio = models.ForeignKey(Anuncio, on_delete=models.CASCADE)
    data = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField() 