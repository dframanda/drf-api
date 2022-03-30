from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from agenda.models import Agendamento
from agenda.serializers import AgendamentoSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response

from datetime import date, datetime, timedelta

# Create your views here.
@api_view(http_method_names=["GET", "PATCH", "DELETE"])
def agendamento_detail(request, id):
    obj = get_object_or_404(Agendamento, id=id)
    obj.cancelado = False
    if request.method == "GET":
        serializer = AgendamentoSerializer(obj)
        return JsonResponse(serializer.data)
    if request.method == "PATCH":
        serializer = AgendamentoSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=200)
        return JsonResponse(serializer.errors, status=400)
    if request.method == "DELETE":
        obj.cancelado = True
        lista_cancelados = obj.delete()
        return Response(status=204)

@api_view(http_method_names=["GET", "POST"])
def agendamento_list(request):
    if request.method == "GET":
        qs = Agendamento.objects.all()
        serializer = AgendamentoSerializer(qs, many=True)
        return JsonResponse(serializer.data, safe=False)
    if request.method == "POST":
        data = request.data
        serializer = AgendamentoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

@api_view(http_method_names=["GET"])
def horarios_list(request, data):

    data = datetime.strptime(data, '%Y-%m-%d').date()
    qs = Agendamento.objects.filter(data_horario__date=data).order_by('data_horario__time')
    serializer = AgendamentoSerializer(qs, many=True)
    delta = timedelta(minutes=30)

    horarios_list = []

    abertura = datetime(data.year, data.month, data.day, 9, 00)
    encerramento = datetime(data.year, data.month, data.day, 18, 00)
    encerramento_sabado = datetime(data.year, data.month, data.day, 13, 00)
    horario_de_almoco = datetime(data.year, data.month, data.day, 12, 00)
    volta_do_almoco = datetime(data.year, data.month, data.day, 13, 00)

    if data.weekday() == 6:
        horarios_list.append({
            'Informação': 'O estabelecimento não abre aos domingos.'
        })

    if data.weekday() == 5:
        while abertura != encerramento_sabado:
            horarios_list.append({
                'data_horario': abertura
            })

            abertura += delta

    if data.weekday() != 5 and data.weekday() != 6:
        while abertura != encerramento:
            horarios_list.append({
                'data_horario': abertura
            })

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
        e = e.get('data_horario')
        horario_e = e[11:16]
        for time in horarios_list:
            data_horario = time.get('data_horario')
            horario_list = datetime.strftime(data_horario, '%H:%M')
            if horario_e == horario_list:
                horarios_list.remove(time)

        return JsonResponse(horarios_list, safe=False)    
    return JsonResponse(serializer.errors, status=400)