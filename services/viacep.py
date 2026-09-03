import requests


def consultar_cep(cep):
    """
    Consulta um CEP na API externa ViaCEP.
    """

    cep_limpo = "".join(filter(str.isdigit, cep))

    if len(cep_limpo) != 8:
        return {
            "sucesso": False,
            "erro": "O CEP deve possuir 8 dígitos."
        }

    url = f"https://viacep.com.br/ws/{cep_limpo}/json/"

    try:
        resposta = requests.get(url, timeout=5)

        if resposta.status_code != 200:
            return {
                "sucesso": False,
                "erro": "Não foi possível consultar o serviço ViaCEP."
            }

        dados = resposta.json()

        if dados.get("erro"):
            return {
                "sucesso": False,
                "erro": "CEP não encontrado."
            }

        return {
            "sucesso": True,
            "dados": {
                "cep": dados.get("cep"),
                "logradouro": dados.get("logradouro"),
                "complemento": dados.get("complemento"),
                "bairro": dados.get("bairro"),
                "cidade": dados.get("localidade"),
                "uf": dados.get("uf"),
                "ibge": dados.get("ibge"),
            }
        }

    except requests.RequestException:
        return {
            "sucesso": False,
            "erro": "Erro de comunicação com o serviço ViaCEP."
        }
