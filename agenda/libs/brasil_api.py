from datetime import date
import requests
from django.conf import settings
import logging


def is_feriado(data: date):
    logging.info(f"Fazendo requisição para BrasilAPI para a data: {data.isoformat()}")
    if settings.TESTING == True:
        logging.info("Requisição não está sendo feita pois TESTING = True")
        if date.day == 15 and date.month == 4:
            return True
        return False

    ano = data.year
    r = requests.get(f"https://brasilapi.com.br/api/feriados/v1/{ano}")

    if not r.status_code == 200:
        logging.error("Algum erro ocorreu na Brasil API")
        return False
    feriados = r.json()
    for feriado in feriados:
        data_feriado_str = feriado["date"]
        data_feriado = date.fromisoformat(data_feriado_str)
        if data == data_feriado:
            return True

    return False
