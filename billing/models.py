from django.db import models
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

class Plan(models.Model):
    PLAN_TYPES = (
        ('basic', 'Básico'),
        ('premium', 'Premium'),
        ('pro', 'Profissional')
    )

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    type = models.CharField(max_length=20, choices=PLAN_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField()
    posts_per_day = models.IntegerField()
    description = models.TextField()
    features = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    checkout_url = models.URLField()  # URL externa do checkout

    def __str__(self):
        return self.name

class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.name}" 

class StripeCustomer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=100)
    subscription_id = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.email} ({self.stripe_customer_id})"

class AnuncioBoost(models.Model):
    anuncio = models.ForeignKey('ads.Anuncio', on_delete=models.CASCADE)
    inicio = models.DateTimeField(auto_now_add=True)
    expira_em = models.DateTimeField()
    stripe_payment_id = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Boost {self.anuncio.titulo}" 