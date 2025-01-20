from django.core.management.base import BaseCommand
from ads.models import Categoria
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Cria categorias iniciais'

    def handle(self, *args, **kwargs):
        categorias = [
            {'nome': 'Imóveis', 'icone': 'fa-home'},
            {'nome': 'Veículos', 'icone': 'fa-car'},
            {'nome': 'Eletrônicos', 'icone': 'fa-laptop'},
            {'nome': 'Móveis', 'icone': 'fa-couch'},
            {'nome': 'Roupas', 'icone': 'fa-tshirt'},
            {'nome': 'Serviços', 'icone': 'fa-briefcase'},
            {'nome': 'Outros', 'icone': 'fa-box'},
        ]

        for cat in categorias:
            Categoria.objects.get_or_create(
                nome=cat['nome'],
                defaults={
                    'slug': slugify(cat['nome']),
                    'icone': cat['icone']
                }
            )

        self.stdout.write(self.style.SUCCESS('Categorias criadas com sucesso!')) 