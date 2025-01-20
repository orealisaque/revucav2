from django.core.management.base import BaseCommand
import json
from users.models import Estado, Cidade
from pathlib import Path

class Command(BaseCommand):
    help = 'Popula o banco de dados com estados e cidades do Brasil'

    def handle(self, *args, **kwargs):
        # Limpa dados existentes
        Estado.objects.all().delete()
        
        # Carrega dados do arquivo JSON
        json_file = Path(__file__).resolve().parent / 'estados_cidades.json'
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Cria estados e cidades
        for estado_data in data:
            estado = Estado.objects.create(
                sigla=estado_data['sigla'],
                nome=estado_data['nome']
            )
            
            for cidade_nome in estado_data['cidades']:
                Cidade.objects.create(
                    nome=cidade_nome,
                    estado=estado
                )
                
        self.stdout.write(self.style.SUCCESS('Estados e cidades importados com sucesso!')) 