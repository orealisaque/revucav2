from django import forms
from .models import Anuncio, AnuncioFoto, AnuncioVideo
from .widgets import ImagePreviewFileInput, VideoPreviewFileInput
from django.core.exceptions import ValidationError

class AnuncioForm(forms.ModelForm):
    fotos = forms.ImageField(
        widget=ImagePreviewFileInput,
        required=False,
        help_text='Selecione uma ou mais fotos',
        label='Fotos'
    )
    
    video = forms.FileField(
        widget=VideoPreviewFileInput,
        required=False,
        help_text='Selecione um vídeo (opcional)',
        label='Vídeo'
    )
    
    class Meta:
        model = Anuncio
        fields = ['titulo', 'descricao', 'preco', 'cidade', 'categoria']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}),
            'preco': forms.NumberInput(attrs={'min': '0', 'step': '0.01'})
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['fotos'].widget.attrs.update({
            'accept': 'image/*',
            'multiple': True,
            'class': 'hidden'
        })
        self.fields['video'].widget.attrs.update({
            'accept': 'video/*',
            'class': 'hidden'
        })

    def clean(self):
        cleaned_data = super().clean()
        fotos = self.files.getlist('fotos')
        videos = self.files.getlist('videos')
        
        if self.user:
            if len(fotos) > self.user.max_fotos:
                raise ValidationError(f'Você pode enviar no máximo {self.user.max_fotos} fotos no seu plano atual.')
                
            if len(videos) > self.user.max_videos:
                raise ValidationError(f'Você pode enviar no máximo {self.user.max_videos} vídeos no seu plano atual.')
            
        return cleaned_data

    def save(self, commit=True):
        anuncio = super().save(commit=False)
        if commit:
            anuncio.save()
        return anuncio 