import re
from datetime import datetime, timedelta, tzinfo
from time import time
from urllib import request

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from agenda.models import (
    Agendamento,
    Estabelecimento,
    Fidelidade,
    Funcionarios,
    Servicos,
)
from agenda.utils import get_horarios_disponiveis


class AgendamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agendamento
        fields = "__all__"

    prestador = serializers.CharField()
    estabelecimento = serializers.CharField()
    servico = serializers.CharField()

    def validate_prestador(self, value):
        try:
            prestador_obj = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Username incorreto!")
        return prestador_obj

    def validate_estabelecimento(self, value):
        try:
            estabelecimento_obj = Estabelecimento.objects.get(
                nome_estabelecimento=value
            )
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Estabelecimento não encontrado!")
        return estabelecimento_obj

    def validate_servico(self, value):
        try:
            servico_obj = Servicos.objects.get(servico=value)
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Serviço não encontrado!")
        return servico_obj

    def validate_data_horario(self, value):
        if value < timezone.now():
            raise serializers.ValidationError(
                "Agendamento não pode ser feito no passado!"
            )
        if value not in get_horarios_disponiveis(value.date()):
            raise serializers.ValidationError("Este horário não está disponível!")

        return value

    def validate(self, attrs):
        nome_cliente = attrs.get("nome_cliente", "")
        data_horario = attrs.get("data_horario", "")
        telefone_cliente = attrs.get("telefone_cliente", "")
        email_cliente = attrs.get("email_cliente", "")
        prestador = attrs.get("prestador", "")
        estabelecimento = attrs.get("estabelecimento", "")
        servico = attrs.get("servico", "")

        if prestador and estabelecimento:
            if not Funcionarios.objects.filter(
                prestador__username=prestador,
                estabelecimento=estabelecimento,
                servico=servico,
            ).exists():
                raise serializers.ValidationError(
                    "Funcionário, estabelecimento ou serviço não estão corretos ou não existem!"
                )

        if data_horario and email_cliente:
            if Agendamento.objects.filter(
                nome_cliente=nome_cliente,
                email_cliente=email_cliente,
                data_horario__date=data_horario,
                prestador__username=prestador,
                estabelecimento=estabelecimento,
                cancelado=False,
            ).exists():
                raise serializers.ValidationError(
                    "Cada cliente pode ter apenas uma reverva por dia!"
                )

        if (
            email_cliente.endswith(".br")
            and telefone_cliente.startswith("+")
            and not telefone_cliente.startswith("+55")
        ):
            raise serializers.ValidationError(
                "E-mail brasileiro deve estar associado a um número do Brasil (+55)"
            )

        return attrs

    def validate_telefone_cliente(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Telefone precisa conter no mínimo 8 dígitos"
            )
        if "+" in value and not value.startswith("+"):
            raise serializers.ValidationError("Formato inválido")
        if not re.sub(r"[^0-9]", "", value).isdigit():
            raise serializers.ValidationError("Telefone deve ser composto por dígitos!")
        return value


class PrestadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "agendamentos"]

    agendamentos = AgendamentoSerializer(many=True, read_only=True)


class FidelidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fidelidade
        fields = "nome_cliente", "nivel_fidelidade"


class FuncionarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funcionarios
        fields = ["estabelecimento", "prestador", "servico"]

    estabelecimento = serializers.CharField()
    prestador = serializers.CharField()
    servico = serializers.CharField()

    def validate_prestador(self, value):
        try:
            prestador_obj = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Prestador não existe!")
        return prestador_obj

    def validate_estabelecimento(self, value):
        try:
            estabelecimento_obj = Estabelecimento.objects.get(
                nome_estabelecimento=value
            )
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Estabelecimento não existe!")
        return estabelecimento_obj

    def validate_servico(self, value):
        try:
            servico_obj = Servicos.objects.get(servico=value)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                "O serviço informado está incorreto ou não existe!"
            )
        return servico_obj

    def validate(self, attrs):
        prestador = attrs.get("prestador", "")
        estabelecimento = attrs.get("estabelecimento", "")
        servico = attrs.get("servico", "")

        servico = Servicos.objects.filter(servico=servico).first()

        if servico:
            if Funcionarios.objects.filter(
                prestador__username=prestador,
                estabelecimento=estabelecimento,
                servico=servico,
            ).exists():
                raise serializers.ValidationError(
                    "O funcionário já está cadastrado neste estabelecimento com o serviço informado!"
                )

        return attrs


class EstabelecimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estabelecimento
        fields = "__all__"

    nome_estabelecimento = serializers.CharField()


class ServicosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicos
        fields = "__all__"

    servico = serializers.CharField()

    def validate(self, attrs):
        servico_request = attrs.get("servico", "")

        if Servicos.objects.filter(servico=servico_request).exists():
            raise serializers.ValidationError("O serviço informado já existe!")

        return attrs
