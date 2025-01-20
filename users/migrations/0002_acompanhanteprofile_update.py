from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        # Adiciona os novos campos
        migrations.AddField(
            model_name='acompanhanteprofile',
            name='nome_completo',
            field=models.CharField(max_length=100, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='acompanhanteprofile',
            name='biografia',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='acompanhanteprofile',
            name='foto',
            field=models.ImageField(upload_to='fotos/', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='acompanhanteprofile',
            name='whatsapp',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='acompanhanteprofile',
            name='instagram',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ] 