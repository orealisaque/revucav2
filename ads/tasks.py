from django.utils import timezone
from .models import Anuncio

def expire_boosts():
    """Expira boosts que passaram do prazo"""
    anuncios = Anuncio.objects.filter(
        is_boosted=True,
        boost_expira_em__lte=timezone.now()
    )
    for anuncio in anuncios:
        anuncio.is_boosted = False
        anuncio.save() 