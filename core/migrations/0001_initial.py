# Generated by Django 5.1.5 on 2025-01-17 10:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Conquista',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('descricao', models.TextField()),
                ('pontos', models.IntegerField()),
                ('icone', models.ImageField(upload_to='conquistas/')),
            ],
            options={
                'verbose_name': 'Conquista',
                'verbose_name_plural': 'Conquistas',
            },
        ),
        migrations.CreateModel(
            name='ConquistaUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_conquista', models.DateTimeField(auto_now_add=True)),
                ('conquista', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.conquista')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Conquista do Usuário',
                'verbose_name_plural': 'Conquistas dos Usuários',
            },
        ),
    ]
