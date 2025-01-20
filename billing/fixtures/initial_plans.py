from django.core.management.base import BaseCommand
from billing.models import Plan

class Command(BaseCommand):
    help = 'Cria os planos iniciais'

    def handle(self, *args, **kwargs):
        plans = [
            {
                'name': 'Básico',
                'slug': 'basico',
                'type': 'basic',
                'price': 55.00,
                'duration_days': 7,
                'posts_per_day': 6,
                'description': 'Plano básico com 6 subidas por dia',
                'features': [
                    'Até 6 subidas automáticas por dia',
                    'Duração de 7 dias',
                    'Suporte via email'
                ]
            },
            {
                'name': 'Premium',
                'slug': 'premium',
                'type': 'premium', 
                'price': 85.00,
                'duration_days': 7,
                'posts_per_day': 12,
                'description': 'Plano premium com 12 subidas por dia',
                'features': [
                    'Até 12 subidas automáticas por dia',
                    'Duração de 7 dias',
                    'Suporte prioritário',
                    'Destaque na listagem'
                ]
            },
            {
                'name': 'Profissional',
                'slug': 'profissional',
                'type': 'pro',
                'price': 130.00,
                'duration_days': 7,
                'posts_per_day': 24,
                'description': 'Plano profissional com 24 subidas por dia',
                'features': [
                    'Até 24 subidas automáticas por dia',
                    'Duração de 7 dias',
                    'Suporte VIP 24/7',
                    'Destaque máximo na listagem',
                    'Estatísticas avançadas'
                ]
            }
        ]

        for plan_data in plans:
            Plan.objects.get_or_create(
                slug=plan_data['slug'],
                defaults=plan_data
            )

        self.stdout.write(self.style.SUCCESS('Planos criados com sucesso!')) 