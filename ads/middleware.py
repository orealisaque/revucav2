from django.shortcuts import redirect
from django.contrib import messages

class AnuncioLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/anuncios/novo/'):
            if request.user.is_authenticated:
                anuncios = request.user.anuncio_set
                fotos_count = sum(a.fotos.count() for a in anuncios.all())
                videos_count = sum(a.videos.count() for a in anuncios.all())
                
                if fotos_count >= request.user.max_fotos:
                    messages.error(request, 'Você atingiu o limite de fotos do seu plano.')
                    return redirect('billing:upgrade')
                    
                if videos_count >= request.user.max_videos:
                    messages.error(request, 'Você atingiu o limite de vídeos do seu plano.')
                    return redirect('billing:upgrade')
                    
        return self.get_response(request) 