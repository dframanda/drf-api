from django.db import models

# Create your models here.


class Fidelidade(models.Model):
    nome_cliente = models.CharField(max_length=200)
    prestador = models.ForeignKey(
        "auth.User", related_name="fidelidade", on_delete=models.CASCADE
    )
    nivel_fidelidade = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["nome_cliente", "prestador", "nivel_fidelidade"],
                name="fidelidade_unique",
            )
        ]

    def __str__(self):
        return self.nome_cliente


class Servicos(models.Model):
    servico = models.CharField(max_length=300, unique=True)

    def __str__(self):
        return self.servico


class Estabelecimento(models.Model):
    nome_estabelecimento = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.nome_estabelecimento


class Funcionarios(models.Model):
    prestador = models.ForeignKey(
        "auth.User", related_name="funcionarios", on_delete=models.CASCADE
    )
    servico = models.ForeignKey(Servicos, on_delete=models.CASCADE)
    estabelecimento = models.ForeignKey(Estabelecimento, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.prestador} -> {self.estabelecimento}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["prestador", "estabelecimento"],
                name="funcionario_unique",
            )
        ]


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
    servico = models.ForeignKey(Servicos, on_delete=models.CASCADE)
    estabelecimento = models.ForeignKey(Estabelecimento, on_delete=models.CASCADE)


class Endereco(models.Model):
    estabelecimento = models.ForeignKey(Estabelecimento, on_delete=models.CASCADE)
    cep = models.CharField(max_length=9)
    estado = models.CharField(max_length=2)
    cidade = models.CharField(max_length=50)
    bairro = models.CharField(max_length=50)
    rua = models.CharField(max_length=200)
    complemento = models.CharField(max_length=50, blank=True)
