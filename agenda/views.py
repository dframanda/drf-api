from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from agenda.models import Agendamento
from agenda.serializers import AgendamentoSerializer
from rest_framework.decorators import api_view

# Create your views here.
@api_view(http_method_names=["GET"])
def agendamento_detail(request, id):
    obj = get_object_or_404(Agendamento, id=id)
    serializer = AgendamentoSerializer(obj) #representacao json, ele vai buscar encontrar nesses campos os mesmos 
    #atributos da classe Agendamento no serializers (por isso mantemos os mesmos nomes)
    return JsonResponse(serializer.data)
    
@api_view(http_method_names=["GET", "POST"])
def agendamento_list(request):
    if request.method == "GET":
        qs = Agendamento.objects.all() #queryset
        serializer = AgendamentoSerializer(qs, many=True)
        return JsonResponse(serializer.data, safe=False)
    if request.method == "POST":
        data = request.data # {"nome_cliente": "Gabriel" ...}
        serializer = AgendamentoSerializer(data=data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            Agendamento.objects.create(
                data_horario=validated_data["data_horario"],
                nome_cliente=validated_data["nome_cliente"],
                email_cliente=validated_data["email_cliente"],
                telefone_cliente=validated_data["telefone_cliente"],
            )
            return JsonResponse(serializer.data, status=201) #status 201 significa created
        return JsonResponse(serializer.errors, status=400)