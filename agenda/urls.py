from django.urls import path

from agenda.views import (
    AgendamentoDetail,
    AgendamentoList,
    PrestadorList,
    horarios_list,
    FidelidadeList,
)

urlpatterns = [
    path("agendamentos/", AgendamentoList.as_view()),
    path("agendamentos/<int:id>/", AgendamentoDetail.as_view()),
    path("horarios/<str:data>/", horarios_list),
    path("prestadores/", PrestadorList.as_view()),
    path("fidelidade/", FidelidadeList.as_view()),
]
