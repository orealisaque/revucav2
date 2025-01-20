from django.db import migrations

def create_initial_data(apps, schema_editor):
    Estado = apps.get_model('users', 'Estado')
    Cidade = apps.get_model('users', 'Cidade')
    
    # Criando São Paulo
    sp = Estado.objects.create(nome='São Paulo', sigla='SP')
    
    # Criando algumas cidades de SP
    cidades_sp = [
        'São Paulo',
        'Campinas',
        'Santos',
        'São José dos Campos',
        'Ribeirão Preto',
        'Franco da Rocha',
        'Guarulhos',
        'Osasco',
        'Santo André',
        'São Bernardo do Campo'
    ]
    
    for cidade in cidades_sp:
        Cidade.objects.create(nome=cidade, estado=sp)

def reverse_initial_data(apps, schema_editor):
    Estado = apps.get_model('users', 'Estado')
    Estado.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_acompanhanteprofile_complete'),
    ]

    operations = [
        migrations.RunPython(create_initial_data, reverse_initial_data),
    ] 