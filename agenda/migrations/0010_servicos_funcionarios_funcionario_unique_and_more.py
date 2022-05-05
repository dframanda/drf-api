# Generated by Django 4.0.2 on 2022-04-09 19:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0009_estabelecimento_funcionarios_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Servicos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('servico', models.CharField(max_length=250)),
            ],
        ),
        migrations.AddConstraint(
            model_name='funcionarios',
            constraint=models.UniqueConstraint(fields=('prestador', 'estabelecimento'), name='funcionario_unique'),
        ),
        migrations.AlterField(
            model_name='funcionarios',
            name='servicos',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agenda.servicos'),
        ),
    ]