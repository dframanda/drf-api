from django.db import models

# Create your models here.
class Agendamento(models.Model):
    STATES_CHOICES = [
        ("CONF", "CONFIRMATED"),
        ("UNCO", "UNCONFIRMATED"),
        ("EXEC", "EXECUTED"),
        ("CANC", "CANCELED"),
    ]

    prestador = models.ForeignKey(
        "auth.User", related_name="agendamentos", on_delete=models.CASCADE
    )
    data_horario = models.DateTimeField()
    nome_cliente = models.CharField(max_length=200)
    email_cliente = models.EmailField()
    telefone_cliente = models.CharField(max_length=20)
    states = models.CharField(max_length=4, choices=STATES_CHOICES, default="UNCO")
    cancelado = models.BooleanField(default=False)
