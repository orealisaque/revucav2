from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        # Adiciona apenas os campos que faltam
        migrations.AddField(
            model_name='acompanhanteprofile',
            name='estado',
            field=models.ForeignKey(
                to='users.Estado',
                on_delete=django.db.models.deletion.SET_NULL,
                null=True,
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='acompanhanteprofile',
            name='cidade',
            field=models.ForeignKey(
                to='users.Cidade',
                on_delete=django.db.models.deletion.SET_NULL,
                null=True,
                blank=True
            ),
        ),
    ] 