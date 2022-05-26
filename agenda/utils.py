from multiprocessing.sharedctypes import Value
from typing import Iterable
from datetime import date, datetime, timedelta, timezone

import requests
import logging
from agenda.models import Agendamento
from agenda.libs import brasil_api


def get_horarios_disponiveis(data: date) -> Iterable[datetime]:

    if brasil_api.is_feriado(data) or data.weekday() == 6:
        return []

    inicio = datetime(data.year, data.month, data.day, 9, 0, tzinfo=timezone.utc)
    fim = datetime(data.year, data.month, data.day, 18, 00, tzinfo=timezone.utc)
    fim_sabado = datetime(data.year, data.month, data.day, 13, 00, tzinfo=timezone.utc)
    inicio_pausa = datetime(
        data.year, data.month, data.day, 12, 00, tzinfo=timezone.utc
    )
    fim_pausa = datetime(data.year, data.month, data.day, 13, 00, tzinfo=timezone.utc)
    delta = timedelta(minutes=30)
    horarios_disponiveis = []

    if data.weekday() == 5:
        while inicio < fim_sabado:
            if not Agendamento.objects.filter(
                data_horario=inicio, states="CONF"
            ).exists():
                horarios_disponiveis.append(inicio)
            inicio = inicio + delta
    else:
        while inicio < fim:
            if not Agendamento.objects.filter(
                data_horario=inicio, states="CONF"
            ).exists():
                if not inicio_pausa <= inicio < fim_pausa:
                    horarios_disponiveis.append(inicio)
            inicio = inicio + delta

    return horarios_disponiveis


def verifica_cep(cep: str):
    logging.info(f"Fazendo requisição para BrasilAPI com o CEP: {cep}")

    r = requests.get(f"https://brasilapi.com.br/api/cep/v2/{cep}")

    if not r.status_code == 200:
        logging.error("Algum erro ocorreu na Brasil API")
        return False

    info = r.json()
    return info
