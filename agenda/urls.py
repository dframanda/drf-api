from django.urls import path

from agenda.views import (
    AgendamentoDetail,
    AgendamentoList,
    ServicosList,
    EstabelecimentoList,
    FuncionarioList,
    PrestadorList,
    FidelidadeList,
    get_horarios,
)

urlpatterns = [
    path("agendamentos/", AgendamentoList.as_view(), name="agendamento_list"),
    path("agendamentos/<int:id>/", AgendamentoDetail.as_view()),
    path("horarios/", get_horarios),
    path("prestadores/", PrestadorList.as_view()),
    path("fidelidade/", FidelidadeList.as_view()),
    path("funcionarios/", FuncionarioList.as_view()),
    path("estabelecimentos/", EstabelecimentoList.as_view()),
    path("servicos/", ServicosList.as_view()),
]
