from django.db import models
from django.conf import settings
from ads.models import Anuncio

class ModerationLog(models.Model):
    ACTIONS = (
        ('approve', 'Aprovado'),
        ('reject', 'Rejeitado'),
        ('suspend', 'Suspenso'),
    )

    anuncio = models.ForeignKey(Anuncio, on_delete=models.CASCADE)
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTIONS)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Log de Moderação'
        verbose_name_plural = 'Logs de Moderação' 