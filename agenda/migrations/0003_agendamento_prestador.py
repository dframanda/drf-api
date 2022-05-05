# Generated by Django 4.0.2 on 2022-03-31 18:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('agenda', '0002_rename_email_clente_agendamento_email_cliente'),
    ]

    operations = [
        migrations.AddField(
            model_name='agendamento',
            name='prestador',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='agendamentos', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]