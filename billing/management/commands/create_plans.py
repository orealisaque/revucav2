from django.core.management.base import BaseCommand
from billing.models import Plan

class Command(BaseCommand):
    help = 'Cria os planos padrão no sistema'

    def handle(self, *args, **kwargs):
        plans = [
            {
                'name': 'Plano Básico',
                'slug': 'basico',
                'stripe_price_id': 'price_xxxxx',  # Substitua pelo ID real
                'price': 29.90,
                'interval': 'month',
                'features': {
                    'Anúncios ativos': '2',
                    'Fotos por anúncio': '3',
                    'Suporte por email': 'Sim',
                }
            },
            {
                'name': 'Plano Profissional',
                'slug': 'profissional',
                'stripe_price_id': 'price_yyyyy',  # Substitua pelo ID real
                'price': 59.90,
                'interval': 'month',
                'features': {
                    'Anúncios ativos': '5',
                    'Fotos por anúncio': '5',
                    'Suporte prioritário': 'Sim',
                    'Destaque na busca': 'Sim',
                }
            },
            {
                'name': 'Plano Premium',
                'slug': 'premium',
                'stripe_price_id': 'price_zzzzz',  # Substitua pelo ID real
                'price': 99.90,
                'interval': 'month',
                'features': {
                    'Anúncios ativos': 'Ilimitados',
                    'Fotos por anúncio': '10',
                    'Suporte VIP': 'Sim',
                    'Destaque na busca': 'Sim',
                    'Estatísticas avançadas': 'Sim',
                }
            },
        ]

        for plan_data in plans:
            Plan.objects.get_or_create(
                slug=plan_data['slug'],
                defaults=plan_data
            )
            self.stdout.write(
                self.style.SUCCESS(f'Plano "{plan_data["name"]}" criado com sucesso!')
            ) 