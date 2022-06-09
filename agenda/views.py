from datetime import date, datetime, timedelta
import email
from genericpath import exists
from django.utils import timezone

from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import generics, permissions, serializers
from rest_framework.decorators import api_view

from agenda.models import (
    Agendamento,
    Endereco,
    Fidelidade,
    Funcionarios,
    Estabelecimento,
    Servicos,
)
from agenda.serializers import (
    AgendamentoSerializer,
    EnderecoSerializer,
    EstabelecimentoSerializer,
    FidelidadeSerializer,
    FuncionarioSerializer,
    PrestadorSerializer,
    ServicosSerializer,
)
from agenda.utils import get_horarios_disponiveis


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

        serializer = AgendamentoSerializer(data=request.data)
        data = request.data
        nome_cliente = data["nome_cliente"]
        prestador_request = data["prestador"]
        prestador = User.objects.filter(username=prestador_request).first()
        estabelecimento = data["estabelecimento"]
        fidelidade_usuario = Fidelidade.objects.filter(
            nome_cliente=nome_cliente, prestador__username=prestador_request
        )

        estabelecimento_obj = Estabelecimento.objects.filter(
            nome_estabelecimento=estabelecimento
        )

        if serializer.is_valid():
            if estabelecimento_obj.exists():
                if Funcionarios.objects.filter(
                    prestador__username=prestador_request,
                    estabelecimento=estabelecimento_obj.first(),
                ).exists():
                    if fidelidade_usuario.exists():
                        fidelidade_usuario = fidelidade_usuario.first()
                        fidelidade_usuario.nivel_fidelidade += 1
                        fidelidade_usuario.save()
                    else:
                        Fidelidade.objects.create(
                            nome_cliente=nome_cliente, prestador=prestador
                        )

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


class FuncionarioList(generics.ListCreateAPIView):
    serializer_class = FuncionarioSerializer
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        data = request.data
        estabelecimento_request = data["estabelecimento"]
        prestador_request = data["prestador"]
        servico_request = data["servico"]

        estabelecimento = Estabelecimento.objects.filter(
            nome_estabelecimento=estabelecimento_request
        ).first()
        prestador = User.objects.filter(username=prestador_request).first()
        servico = Servicos.objects.filter(servico=servico_request).first()

        if servico:
            if not Funcionarios.objects.filter(
                estabelecimento=estabelecimento, prestador=prestador, servico=servico
            ).exists():
                Funcionarios.objects.create(
                    estabelecimento=estabelecimento,
                    prestador=prestador,
                    servico=servico,
                )

        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        estabelecimento = self.request.query_params.get("estabelecimento", None)
        return Funcionarios.objects.filter(estabelecimento=estabelecimento)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            if request.user.is_staff:
                return True
        if request.method == "GET":
            return True
        return False


class EstabelecimentoList(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = EstabelecimentoSerializer

    def get_queryset(self):
        return Estabelecimento.objects.all()


class ServicosList(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = ServicosSerializer

    def get_queryset(self):
        return Servicos.objects.all()


class EnderecoList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = EnderecoSerializer

    def get_queryset(self):
        return Endereco.objects.all()


@api_view(http_method_names=["GET"])
def get_horarios(request):
    data = request.query_params.get("data")
    if not data:
        data = datetime.now().date()
    else:
        data = datetime.fromisoformat(data).date()

    horarios_disponiveis = sorted(list(get_horarios_disponiveis(data)))
    return JsonResponse(horarios_disponiveis, safe=False)


@api_view(http_method_names=["GET"])
def healthcheck(request):
    return Response({"status": "OK", "message": "Deployado!"}, status=200)


@api_view(http_method_names=["GET", "POST"])
def users(request):
    if request.method == "POST":
        data = request.data
        username = data["username"]
        senha = data["senha"]
        email = data["email"]

        if not username:
            raise serializers.ValidationError("É necessário informar o nome de usuário")

        if not senha:
            raise serializers.ValidationError("É necessário informar uma senha!")

        if not email:
            raise serializers.ValidationError("É necessário informar um email!")

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Nome de usuário já existe!")

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email já existe!")

        user_obj = User.objects.create_user(
            username=username, password=senha, email=email, is_staff=False
        )

        obj = {
            "id": user_obj.id,
            "username": user_obj.username,
            "email": user_obj.email,
            "is_staff": user_obj.is_staff,
        }

        return JsonResponse(obj, safe=False)

    if request.method == "GET":
        qs = User.objects.all()
        users_list = []

        for user in qs:
            users_list.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_staff": user.is_staff,
                }
            )

        return JsonResponse(users_list, safe=False)
