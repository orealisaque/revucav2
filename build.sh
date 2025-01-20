#!/usr/bin/env bash
# exit on error
set -o errexit

# Instala dependências
pip install -r requirements.txt

# Coleta arquivos estáticos
python manage.py collectstatic --no-input

# Aplica migrações
python manage.py migrate 