import re
from datetime import datetime, timedelta, tzinfo
from time import time
from urllib import request

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers

from agenda.models import Agendamento, Fidelidade


class AgendamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agendamento
        fields = [
            "id",
            "data_horario",
            "nome_cliente",
            "email_cliente",
            "telefone_cliente",
            "prestador",
            "states",
        ]

    prestador = serializers.CharField()

    def validate_prestador(self, value):
        try:
            prestador_obj = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Username não existe!")
        return prestador_obj

    def validate_data_horario(self, value):
        if value < timezone.now():
            raise serializers.ValidationError(
                "Agendamento não pode ser feito no passado!"
            )

        if value:
            data_request = datetime.fromisoformat(str(value))
            queryset = Agendamento.objects.filter(cancelado=False)
            timeDelta = timedelta(minutes=30)

            inicio_pausa = datetime(
                data_request.year,
                data_request.month,
                data_request.day,
                12,
                tzinfo=timezone.utc,
            )
            fim_pausa = datetime(
                data_request.year,
                data_request.month,
                data_request.day,
                13,
                tzinfo=timezone.utc,
            )
            inicio_expediente = datetime(
                data_request.year,
                data_request.month,
                data_request.day,
                9,
                tzinfo=timezone.utc,
            )
            fim_expediente = datetime(
                data_request.year,
                data_request.month,
                data_request.day,
                18,
                tzinfo=timezone.utc,
            )
            fim_expediente_sabado = datetime(
                data_request.year,
                data_request.month,
                data_request.day,
                13,
                tzinfo=timezone.utc,
            )

            if (
                data_request.weekday() != 6
                and data_request.weekday() != 5
                and data_request >= inicio_pausa
                and data_request < fim_pausa
            ):
                raise serializers.ValidationError(
                    "Não é possível marcar um agendamento no horário de almoço!"
                )
            if data_request.weekday() == 6:
                raise serializers.ValidationError(
                    "O estabelecimento não funciona aos domingos!"
                )
            if data_request.weekday() != 5 and data_request >= fim_expediente:
                raise serializers.ValidationError(
                    "O estabelecimento funciona apenas até 18h!"
                )
            if data_request.weekday() == 5 and data_request > fim_expediente_sabado:
                raise serializers.ValidationError(
                    "O estabelecimento funciona somente até 13h aos sábados!"
                )
            if data_request < inicio_expediente:
                raise serializers.ValidationError(
                    "O estabelecimento abre apenas às 9h!"
                )

            for e in queryset:
                date_intern = datetime.date(e.data_horario)

                if date_intern == data_request.date():
                    if (
                        e.data_horario <= data_request - timeDelta
                        or e.data_horario >= data_request + timeDelta
                    ):
                        pass
                    elif e.states == "CONF":
                        raise serializers.ValidationError(
                            "O horário selecionado não está disponível!"
                        )
        return value

    def validate(self, attrs):
        nome_cliente = attrs.get("nome_cliente", "")
        data_horario = attrs.get("data_horario", "")
        telefone_cliente = attrs.get("telefone_cliente", "")
        email_cliente = attrs.get("email_cliente", "")
        prestador = attrs.get("prestador", "")

        if data_horario and email_cliente:
            if Agendamento.objects.filter(
                nome_cliente=nome_cliente,
                email_cliente=email_cliente,
                data_horario__date=data_horario,
                prestador__username=prestador,
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

