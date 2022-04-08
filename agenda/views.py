from datetime import date, datetime, timedelta
from genericpath import exists
from django.utils import timezone

from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import generics, permissions
from rest_framework.decorators import api_view

from agenda.models import Agendamento, Fidelidade
from agenda.serializers import (
    AgendamentoSerializer,
    FidelidadeSerializer,
    PrestadorSerializer,
)


class IsOwnerOrCreateOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            return True
        username = request.query_params.get("username", None)
        if request.user.username == username:
            return True
        return False


class IsPrestador(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.prestador == request.user:
            return True
        return False


class AgendamentoList(generics.ListCreateAPIView):
    serializer_class = AgendamentoSerializer
    permission_classes = [IsOwnerOrCreateOnly]

    def post(self, request, *args, **kwargs):
        data = request.data
        data_horario = data["data_horario"]
        nome_cliente = data["nome_cliente"]
        email_cliente = data["email_cliente"]
        telefone_cliente = data["telefone_cliente"]
        prestador_request = data["prestador"]
        prestador = User.objects.filter(username=prestador_request).first()

        fidelidade_usuario = Fidelidade.objects.filter(
            nome_cliente=nome_cliente, prestador__username=prestador_request
        )

        if fidelidade_usuario.exists():
            fidelidade_usuario = fidelidade_usuario.first()
            fidelidade_usuario.nivel_fidelidade += 1
            fidelidade_usuario.save()
        else:
            Fidelidade.objects.create(nome_cliente=nome_cliente, prestador=prestador)

        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        executado = self.request.query_params.get("executado", None)
        confirmado = self.request.query_params.get("confirmado", None)
        if confirmado == "True" or confirmado == "true":
            username = self.request.query_params.get("username", None)
            return Agendamento.objects.filter(
                prestador__username=username, states="CONF", cancelado=False
            )
        if confirmado == "False" or confirmado == "false":
            username = self.request.query_params.get("username", None)
            return Agendamento.objects.filter(
                prestador__username=username, states="UNCO", cancelado=False
            )
        if executado == "True" or executado == "true":
            username = self.request.query_params.get("username", None)
            data = timezone.now()
            return Agendamento.objects.filter(
                prestador__username=username,
                data_horario__lt=data,
                states="CONF",
                cancelado=False,
            )
        else:
            username = self.request.query_params.get("username", None)
            return Agendamento.objects.filter(
                prestador__username=username, cancelado=False
            )


class AgendamentoDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsPrestador]
    queryset = Agendamento.objects.filter(cancelado=False)
    serializer_class = AgendamentoSerializer
    lookup_field = "id"  # pk

    def perform_destroy(self, instance):
        instance.cancelado = True
        instance.save()


class FidelidadeList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FidelidadeSerializer

    def get_queryset(self):
        username = self.request.query_params.get("username", None)
        return Fidelidade.objects.filter(prestador__username=username)


class PrestadorList(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = PrestadorSerializer
    queryset = User.objects.all()


@api_view(http_method_names=["GET"])
def horarios_list(request, data):

    data = datetime.strptime(data, "%Y-%m-%d").date()
    qs = Agendamento.objects.filter(data_horario__date=data).order_by(
        "data_horario__time"
    )
    serializer = AgendamentoSerializer(qs, many=True)
    delta = timedelta(minutes=30)

    horarios_list = []

    abertura = datetime(data.year, data.month, data.day, 9, 00)
    encerramento = datetime(data.year, data.month, data.day, 18, 00)
    encerramento_sabado = datetime(data.year, data.month, data.day, 13, 00)
    horario_de_almoco = datetime(data.year, data.month, data.day, 12, 00)
    volta_do_almoco = datetime(data.year, data.month, data.day, 13, 00)

    if data.weekday() == 6:
        horarios_list.append({"Informação": "O estabelecimento não abre aos domingos."})

    if data.weekday() == 5:
        while abertura != encerramento_sabado:
            horarios_list.append({"data_horario": abertura})

            abertura += delta

    if data.weekday() != 5 and data.weekday() != 6:
        while abertura != encerramento:
            horarios_list.append({"data_horario": abertura})

            if abertura == horario_de_almoco:
                if horario_de_almoco < volta_do_almoco:
                    horarios_list.pop()
                    horario_de_almoco += delta

            abertura += delta

    if horario_de_almoco in horarios_list:
        while horario_de_almoco != volta_do_almoco:
            horarios_list.remove(horario_de_almoco)

            horario_de_almoco += delta

    for e in serializer.data:
        e = e.get("data_horario")
        horario_e = e[11:16]
        for time in horarios_list:
            data_horario = time.get("data_horario")
            horario_list = datetime.strftime(data_horario, "%H:%M")
            if horario_e == horario_list:
                horarios_list.remove(time)

        return JsonResponse(horarios_list, safe=False)
    return JsonResponse(serializer.errors, status=400)
