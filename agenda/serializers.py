import re
from datetime import datetime, timedelta, tzinfo
from time import time
from urllib import request
import logging

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from agenda.models import (
    Agendamento,
    Endereco,
    Estabelecimento,
    Fidelidade,
    Funcionarios,
    Servicos,
)
from agenda.utils import get_horarios_disponiveis, verifica_cep


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

    def validate(self, attrs):
        estabelecimento_request = attrs.get("nome_estabelecimento", "")

        if Estabelecimento.objects.filter(
            nome_estabelecimento=estabelecimento_request
        ).exists():
            raise serializers.ValidationError("O estabelecimento informado já existe!")

        return attrs


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


class EnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = "__all__"

    estabelecimento = serializers.CharField()
    estado = serializers.CharField(default="")
    cidade = serializers.CharField(default="")
    bairro = serializers.CharField(default="")
    rua = serializers.CharField(default="")

    def validate_estabelecimento(self, value):
        try:
            estabelecimento_obj = Estabelecimento.objects.filter(
                nome_estabelecimento=value
            )
        except not estabelecimento_obj.exists():
            raise serializers.ValidationError(
                "O estabelecimento informado não foi encontrado!"
            )

        return estabelecimento_obj.first()

    def validate_cep(self, value):
        verifica_caracteres = re.sub(r"[^0-9]", "", value)

        if value == "":
            raise serializers.ValidationError("O CEP precisa ser informado.")

        if value != verifica_caracteres:
            raise serializers.ValidationError(
                "O CEP precisa ser composto apenas por números!"
            )

        if len(value) != 8:
            raise serializers.ValidationError("O CEP deve ter 8 digítos!")

        validacao_cep = verifica_cep(value)

        if not validacao_cep:
            raise serializers.ValidationError("O CEP informado não é válido!")

        return value

    def validate_estado(self, value):
        if value == "":
            return value

        if len(value) != 2:
            raise serializers.ValidationError("Você deve informar a sigla do Estado!")

        verifica_caracteres = re.sub(r"[^A-Za-z]", "", value)

        if value != verifica_caracteres:
            raise serializers.ValidationError(
                "A sigla do Estado precisa ser composta apenas por letras!"
            )

        return value

    def validate_cidade(self, value):
        if value == "":
            return value

        verifica_caracteres = re.sub(r"[^A-Za-z]", "", value)

        if value != verifica_caracteres:
            raise serializers.ValidationError(
                "A nome da cidade precisa ser composto apenas por letras!"
            )

        return value

    def validate_bairro(self, value):
        if value == "":
            return value

        verifica_caracteres = re.sub(r"[^A-Za-z]", "", value)

        if value != verifica_caracteres:
            raise serializers.ValidationError(
                "O nome do bairro precisa ser composto apenas por letras!"
            )

        return value

    def validate_rua(self, value):
        return value

    def validate_complemento(self, value):
        return value

    def validate(self, attrs):
        cep = attrs.get("cep", None)
        estado = attrs.get("estado", None)
        cidade = attrs.get("cidade", None)
        bairro = attrs.get("bairro", None)
        rua = attrs.get("rua", None)

        verifica_valores = verifica_cep(cep)

        verifica_estado = verifica_valores["state"]
        verifica_cidade = verifica_valores["city"]
        verifica_bairro = verifica_valores["neighborhood"]
        verifica_rua = verifica_valores["street"]

        if cep and rua and cidade and bairro and rua:
            if estado != verifica_estado:
                logging.warning("Estado informado não coincide com o CEP!")
            if cidade != verifica_cidade:
                logging.warning("Cidade informada não coincide com o CEP!")
            if bairro != verifica_bairro:
                logging.warning("Bairro informado não coincide com o CEP!")
            if rua != verifica_rua:
                logging.warning("Rua informada não coincide com o CEP!")

        if not estado and cidade and bairro and rua:
            attrs["state"] = verifica_estado
            attrs["city"] = verifica_cidade
            attrs["neighborhood"] = verifica_bairro
            attrs["street"] = verifica_rua

        return attrs
