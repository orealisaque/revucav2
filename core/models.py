from django.db import models
from users.models import CustomUser

class Conquista(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    pontos = models.IntegerField()
    icone = models.ImageField(upload_to='conquistas/')
    
    class Meta:
        verbose_name = 'Conquista'
        verbose_name_plural = 'Conquistas'

class ConquistaUsuario(models.Model):
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    conquista = models.ForeignKey(Conquista, on_delete=models.CASCADE)
    data_conquista = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Conquista do Usuário'
        verbose_name_plural = 'Conquistas dos Usuários' 