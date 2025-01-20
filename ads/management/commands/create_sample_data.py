from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from ads.models import Anuncio, AnuncioFoto
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Cria dados de exemplo'

    def handle(self, *args, **kwargs):
        # Cria um usuário de teste se não existir
        user, created = User.objects.get_or_create(
            email='teste@example.com',
            defaults={
                'password': make_password('teste123'),
                'is_active': True,
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Usuário criado com sucesso'))

        # Cria alguns anúncios
        anuncios_data = [
            {
                'titulo': 'Apartamento Centro',
                'descricao': 'Lindo apartamento no centro da cidade',
                'preco': Decimal('250000.00'),
                'cidade': 'São Paulo',
                'status': 'aprovado'
            },
            {
                'titulo': 'Casa na Praia',
                'descricao': 'Casa com vista para o mar',
                'preco': Decimal('450000.00'),
                'cidade': 'Rio de Janeiro',
                'status': 'aprovado'
            },
            {
                'titulo': 'Terreno',
                'descricao': 'Terreno plano em condomínio fechado',
                'preco': Decimal('150000.00'),
                'cidade': 'Curitiba',
                'status': 'aprovado'
            }
        ]

        for data in anuncios_data:
            anuncio, created = Anuncio.objects.get_or_create(
                titulo=data['titulo'],
                defaults={
                    'user': user,
                    **data
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Anúncio criado: {anuncio.titulo}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Anúncio já existe: {anuncio.titulo}')
                ) 