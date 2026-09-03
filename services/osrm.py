import requests


def calcular_rota(latitude_origem, longitude_origem,
                  latitude_destino, longitude_destino):
    """
    Calcula uma rota de carro entre dois pontos utilizando o OSRM.
    """

    url = (
        "https://router.project-osrm.org/route/v1/driving/"
        f"{longitude_origem},{latitude_origem};"
        f"{longitude_destino},{latitude_destino}"
    )

    parametros = {
        "overview": "false"
    }

    try:
        resposta = requests.get(
            url,
            params=parametros,
            timeout=10
        )

        if resposta.status_code != 200:
            return {
                "sucesso": False,
                "erro": "Não foi possível consultar o serviço OSRM."
            }

        dados = resposta.json()

        if dados.get("code") != "Ok" or not dados.get("routes"):
            return {
                "sucesso": False,
                "erro": "Não foi possível calcular a rota."
            }

        rota = dados["routes"][0]

        distancia_metros = rota["distance"]
        duracao_segundos = rota["duration"]

        distancia_km = round(
            distancia_metros / 1000,
            2
        )

        duracao_minutos = round(
            duracao_segundos / 60
        )

        return {
            "sucesso": True,
            "distancia_km": distancia_km,
            "duracao_minutos": duracao_minutos
        }

    except requests.RequestException:
        return {
            "sucesso": False,
            "erro": "Erro de comunicação com o serviço OSRM."
        }