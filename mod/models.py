from django.db import models
from django.conf import settings
from ads.models import Anuncio

class Report(models.Model):
    anuncio = models.ForeignKey(Anuncio, on_delete=models.CASCADE)
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pendente'),
            ('resolved', 'Resolvido'),
            ('dismissed', 'Descartado')
        ],
        default='pending'
    )

    class Meta:
        verbose_name = 'Denúncia'
        verbose_name_plural = 'Denúncias'
        ordering = ['-created_at']

    def __str__(self):
        return f"Denúncia de {self.reporter} - {self.get_status_display()}"

class ModerationLog(models.Model):
    anuncio = models.ForeignKey(Anuncio, on_delete=models.CASCADE)
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(
        max_length=20,
        choices=[
            ('approve', 'Aprovado'),
            ('reject', 'Rejeitado'),
            ('suspend', 'Suspenso')
        ]
    )
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Log de Moderação'
        verbose_name_plural = 'Logs de Moderação'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_action_display()} por {self.moderator}" 