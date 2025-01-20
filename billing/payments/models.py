from django.db import models
from django.conf import settings
from django.utils import timezone

class Plan(models.Model):
    INTERVAL_CHOICES = (
        ('month', 'Mensal'),
        ('year', 'Anual'),
    )
    
    name = models.CharField('Nome', max_length=100)
    slug = models.SlugField(unique=True)
    stripe_price_id = models.CharField(max_length=100)
    price = models.DecimalField('Preço', max_digits=10, decimal_places=2)
    interval = models.CharField(choices=INTERVAL_CHOICES, max_length=10)
    features = models.JSONField('Recursos', default=dict)
    is_active = models.BooleanField('Ativo', default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Plano'
        verbose_name_plural = 'Planos'

class Subscription(models.Model):
    STATUS_CHOICES = (
        ('active', 'Ativa'),
        ('past_due', 'Pagamento Pendente'),
        ('canceled', 'Cancelada'),
        ('trialing', 'Em Teste'),
    )
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    stripe_subscription_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    current_period_end = models.DateTimeField()
    cancel_at_period_end = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def is_active(self):
        return (
            self.status in ['active', 'trialing'] and 
            self.current_period_end > timezone.now()
        )
    
    class Meta:
        verbose_name = 'Assinatura'
        verbose_name_plural = 'Assinaturas'

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pendente'),
        ('completed', 'Concluída'),
        ('failed', 'Falhou'),
        ('refunded', 'Reembolsada'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_payment_intent_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'
        ordering = ['-created_at'] 