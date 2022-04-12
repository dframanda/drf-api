from django.contrib import admin
from agenda.models import (
    Agendamento,
    Estabelecimento,
    Fidelidade,
    Funcionarios,
    Servicos,
)

# Register your models here.
admin.site.register(Agendamento)
admin.site.register(Fidelidade)
admin.site.register(Funcionarios)
admin.site.register(Estabelecimento)
admin.site.register(Servicos)
