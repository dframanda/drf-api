from datetime import date
import requests


def is_feriado(data: date) -> bool:
    ano = data.year
    r = requests.get(f"https://brasilapi.com.br/api/feriados/v1/{ano}")

    if r.status_code != 200:
        raise ValueError("Não foi possível consultar os feriados!")
    feriados = r.json()
    for feriado in feriados:
        data_feriado_str = feriado["date"]
        data_feriado = date.fromisoformat(data_feriado_str)
        if data == data_feriado:
            return True

    return False
