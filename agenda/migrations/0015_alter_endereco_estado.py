# Generated by Django 4.0.2 on 2022-05-26 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0014_endereco'),
    ]

    operations = [
        migrations.AlterField(
            model_name='endereco',
            name='estado',
            field=models.CharField(max_length=2),
        ),
    ]