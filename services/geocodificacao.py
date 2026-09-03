import requests


def geocodificar_endereco(endereco):
    """
    Converte um endereço em latitude e longitude utilizando o Nominatim.
    """

    endereco_completo = ", ".join(
        valor
        for valor in [
            endereco.get("logradouro"),
            endereco.get("bairro"),
            endereco.get("cidade"),
            endereco.get("uf"),
            endereco.get("cep"),
            "Brasil"
        ]
        if valor
    )

    parametros = {
        "q": endereco_completo,
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": "LogControl-MVP/1.0"
    }

    try:
        resposta = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params=parametros,
            headers=headers,
            timeout=10
        )

        if resposta.status_code != 200:
            return {
                "sucesso": False,
                "erro": "Não foi possível consultar o serviço Nominatim."
            }

        dados = resposta.json()

        if not dados:
            return {
                "sucesso": False,
                "erro": "Não foi possível localizar o endereço."
            }

        return {
            "sucesso": True,
            "latitude": float(dados[0]["lat"]),
            "longitude": float(dados[0]["lon"])
        }

    except requests.RequestException:
        return {
            "sucesso": False,
            "erro": "Erro de comunicação com o serviço Nominatim."
        }