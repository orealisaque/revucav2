import requests
from django.core.cache import cache

class IBGEService:
    BASE_URL = 'https://servicodados.ibge.gov.br/api/v1'
    
    @staticmethod
    def get_estados():
        cache_key = 'ibge_estados'
        estados = cache.get(cache_key)
        
        if not estados:
            response = requests.get(f'{IBGEService.BASE_URL}/localidades/estados')
            estados = response.json()
            cache.set(cache_key, estados, timeout=60*60*24)  # Cache por 24h
            
        return estados
    
    @staticmethod
    def get_cidades(uf):
        cache_key = f'ibge_cidades_{uf}'
        cidades = cache.get(cache_key)
        
        if not cidades:
            response = requests.get(f'{IBGEService.BASE_URL}/localidades/estados/{uf}/municipios')
            cidades = response.json()
            cache.set(cache_key, cidades, timeout=60*60*24)
            
        return cidades 