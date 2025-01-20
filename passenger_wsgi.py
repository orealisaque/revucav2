import os
import sys

from django.core.wsgi import get_wsgi_application

# Adicione o caminho do seu projeto
sys.path.insert(0, '/home/usuario/seu_projeto')

# Defina as variáveis de ambiente
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

# Inicialize a aplicação
application = get_wsgi_application() 