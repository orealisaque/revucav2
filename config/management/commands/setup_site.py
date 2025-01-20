from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Configura o site padrão'

    def handle(self, *args, **kwargs):
        site = Site.objects.get_or_create(
            pk=1,
            defaults={
                'domain': 'localhost:8000',
                'name': 'Revuca'
            }
        )[0]
        
        if not site.pk == 1:
            site.pk = 1
            site.save()
            
        self.stdout.write(self.style.SUCCESS('Site configurado com sucesso')) 