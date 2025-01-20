from django.core.management.base import BaseCommand
import requests
from users.models import Estado, Cidade

class Command(BaseCommand):
    help = 'Popula estados e cidades usando a API do IBGE'

    def handle(self, *args, **kwargs):
        # Limpa dados existentes
        Estado.objects.all().delete()
        Cidade.objects.all().delete()
        
        # Busca estados
        estados_response = requests.get('https://servicodados.ibge.gov.br/api/v1/localidades/estados')
        estados = estados_response.json()
        
        for estado in estados:
            estado_obj = Estado.objects.create(
                nome=estado['nome'],
                sigla=estado['sigla']
            )
            
            # Busca cidades do estado
            cidades_response = requests.get(f'https://servicodados.ibge.gov.br/api/v1/localidades/estados/{estado["id"]}/municipios')
            cidades = cidades_response.json()
            
            # Cria cidades em lote
            Cidade.objects.bulk_create([
                Cidade(
                    nome=cidade['nome'],
                    estado=estado_obj
                ) for cidade in cidades
            ])
            
            self.stdout.write(
                self.style.SUCCESS(f'Estado {estado["nome"]} e suas cidades foram importados com sucesso!')
            ) 