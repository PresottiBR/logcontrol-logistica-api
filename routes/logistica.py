from flask import Blueprint, jsonify, request

from services.viacep import consultar_cep
from services.geocodificacao import geocodificar_endereco
from services.osrm import calcular_rota
from services.banco import obter_conexao


logistica_bp = Blueprint(
    "logistica",
    __name__,
    url_prefix="/logistica"
)


@logistica_bp.get("/cep/<cep>")
def consultar_endereco_por_cep(cep):
    """
    Consulta um endereço pelo CEP utilizando a ViaCEP.
    ---
    tags:
      - Logística
    parameters:
      - name: cep
        in: path
        type: string
        required: true
        description: CEP que será consultado
        example: "01001000"
    responses:
      200:
        description: Endereço encontrado
      400:
        description: CEP inválido
      404:
        description: CEP não encontrado
      502:
        description: Erro na comunicação com a ViaCEP
    """

    resultado = consultar_cep(cep)

    if not resultado["sucesso"]:
        erro = resultado["erro"]

        if erro == "CEP não encontrado.":
            return jsonify({
                "erro": erro
            }), 404

        if erro in [
            "Não foi possível consultar o serviço ViaCEP.",
            "Erro de comunicação com o serviço ViaCEP."
        ]:
            return jsonify({
                "erro": erro
            }), 502

        return jsonify({
            "erro": erro
        }), 400

    return jsonify({
        "mensagem": "CEP consultado com sucesso.",
        "fonte": "ViaCEP",
        "endereco": resultado["dados"]
    }), 200


@logistica_bp.get("/rota")
def calcular_rota_logistica():
    """
    Calcula a distância entre dois CEPs.
    ---
    tags:
      - Logística
    parameters:
      - name: origem
        in: query
        type: string
        required: true
        description: CEP de origem
        example: "01001000"
      - name: destino
        in: query
        type: string
        required: true
        description: CEP de destino
        example: "20040002"
    responses:
      200:
        description: Rota calculada com sucesso
      400:
        description: CEPs não informados ou inválidos
      404:
        description: Um dos CEPs não foi encontrado ou localizado
      502:
        description: Erro em um dos serviços externos
    """

    origem = request.args.get("origem")
    destino = request.args.get("destino")

    if not origem or not destino:
        return jsonify({
            "erro": "Os CEPs de origem e destino são obrigatórios."
        }), 400

    resultado_origem = consultar_cep(origem)

    if not resultado_origem["sucesso"]:
        erro = resultado_origem["erro"]

        if erro == "CEP não encontrado.":
            return jsonify({
                "erro": f"CEP de origem: {erro}"
            }), 404

        if erro in [
            "Não foi possível consultar o serviço ViaCEP.",
            "Erro de comunicação com o serviço ViaCEP."
        ]:
            return jsonify({
                "erro": f"CEP de origem: {erro}"
            }), 502

        return jsonify({
            "erro": f"CEP de origem: {erro}"
        }), 400

    resultado_destino = consultar_cep(destino)

    if not resultado_destino["sucesso"]:
        erro = resultado_destino["erro"]

        if erro == "CEP não encontrado.":
            return jsonify({
                "erro": f"CEP de destino: {erro}"
            }), 404

        if erro in [
            "Não foi possível consultar o serviço ViaCEP.",
            "Erro de comunicação com o serviço ViaCEP."
        ]:
            return jsonify({
                "erro": f"CEP de destino: {erro}"
            }), 502

        return jsonify({
            "erro": f"CEP de destino: {erro}"
        }), 400

    coordenadas_origem = geocodificar_endereco(
        resultado_origem["dados"]
    )

    if not coordenadas_origem["sucesso"]:
        return jsonify({
            "erro": f"Origem: {coordenadas_origem['erro']}"
        }), 404

    coordenadas_destino = geocodificar_endereco(
        resultado_destino["dados"]
    )

    if not coordenadas_destino["sucesso"]:
        return jsonify({
            "erro": f"Destino: {coordenadas_destino['erro']}"
        }), 404

    resultado_rota = calcular_rota(
        coordenadas_origem["latitude"],
        coordenadas_origem["longitude"],
        coordenadas_destino["latitude"],
        coordenadas_destino["longitude"]
    )

    if not resultado_rota["sucesso"]:
        return jsonify({
            "erro": resultado_rota["erro"]
        }), 502

    return jsonify({
        "mensagem": "Rota calculada com sucesso.",
        "origem": {
            "cep": resultado_origem["dados"]["cep"],
            "cidade": resultado_origem["dados"]["cidade"],
            "uf": resultado_origem["dados"]["uf"],
            "endereco": resultado_origem["dados"]
        },
        "destino": {
            "cep": resultado_destino["dados"]["cep"],
            "cidade": resultado_destino["dados"]["cidade"],
            "uf": resultado_destino["dados"]["uf"],
            "endereco": resultado_destino["dados"]
        },
        "rota": {
            "distancia_km": resultado_rota["distancia_km"],
            "duracao_minutos": resultado_rota["duracao_minutos"]
        },
        "servicos_externos": [
            "ViaCEP",
            "Nominatim",
            "OSRM"
        ]
    }), 200


@logistica_bp.post("/enderecos")
def cadastrar_endereco():
    """
    Cadastra um endereço para um cliente.
    ---
    tags:
      - Endereços
    consumes:
      - application/json
    parameters:
      - in: body
        name: endereco
        required: true
        schema:
          type: object
          required:
            - cliente_id
            - cep
            - logradouro
            - numero
            - bairro
            - cidade
            - uf
          properties:
            cliente_id:
              type: integer
              example: 1
            cep:
              type: string
              example: "01001000"
            logradouro:
              type: string
              example: "Praça da Sé"
            numero:
              type: string
              example: "100"
            complemento:
              type: string
              example: "Sala 1"
            bairro:
              type: string
              example: "Sé"
            cidade:
              type: string
              example: "São Paulo"
            uf:
              type: string
              example: "SP"
    responses:
      201:
        description: Endereço cadastrado com sucesso
      400:
        description: Dados obrigatórios não informados
      404:
        description: Cliente não encontrado
      500:
        description: Erro interno no banco de dados
    """

    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({
            "erro": "O corpo da requisição deve possuir dados em JSON."
        }), 400

    campos_obrigatorios = [
        "cliente_id",
        "cep",
        "logradouro",
        "numero",
        "bairro",
        "cidade",
        "uf"
    ]

    campos_faltantes = [
        campo
        for campo in campos_obrigatorios
        if campo not in dados
        or dados[campo] is None
        or str(dados[campo]).strip() == ""
    ]

    if campos_faltantes:
        return jsonify({
            "erro": "Campos obrigatórios não informados.",
            "campos": campos_faltantes
        }), 400

    try:
        cliente_id = int(dados["cliente_id"])
    except (TypeError, ValueError):
        return jsonify({
            "erro": "cliente_id deve ser um número inteiro."
        }), 400

    cep = "".join(filter(str.isdigit, str(dados["cep"])))

    if len(cep) != 8:
        return jsonify({
            "erro": "O CEP deve possuir 8 dígitos."
        }), 400

    uf = str(dados["uf"]).strip().upper()

    if len(uf) != 2:
        return jsonify({
            "erro": "A UF deve possuir 2 caracteres."
        }), 400

    conexao = None

    try:
        conexao = obter_conexao()

        with conexao.cursor() as cursor:

            cursor.execute(
                "SELECT id FROM clientes WHERE id = %s AND ativo = TRUE",
                (cliente_id,)
            )

            cliente = cursor.fetchone()

            if not cliente:
                return jsonify({
                    "erro": "Cliente não encontrado ou inativo."
                }), 404

            cursor.execute(
                """
                INSERT INTO enderecos (
                    cliente_id,
                    cep,
                    logradouro,
                    numero,
                    complemento,
                    bairro,
                    cidade,
                    uf
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    cliente_id,
                    cep,
                    str(dados["logradouro"]).strip(),
                    str(dados["numero"]).strip(),
                    (
                        str(dados["complemento"]).strip()
                        if dados.get("complemento") is not None
                        else None
                    ),
                    str(dados["bairro"]).strip(),
                    str(dados["cidade"]).strip(),
                    uf
                )
            )

            endereco_id = cursor.fetchone()[0]

        conexao.commit()

        return jsonify({
            "mensagem": "Endereço cadastrado com sucesso.",
            "endereco": {
                "id": endereco_id,
                "cliente_id": cliente_id,
                "cep": cep,
                "logradouro": str(dados["logradouro"]).strip(),
                "numero": str(dados["numero"]).strip(),
                "complemento": (
                    str(dados["complemento"]).strip()
                    if dados.get("complemento") is not None
                    else None
                ),
                "bairro": str(dados["bairro"]).strip(),
                "cidade": str(dados["cidade"]).strip(),
                "uf": uf
            }
        }), 201

    except Exception:
        if conexao:
            conexao.rollback()

        return jsonify({
            "erro": "Não foi possível cadastrar o endereço."
        }), 500

    finally:
        if conexao:
            conexao.close()


@logistica_bp.get("/enderecos/<int:endereco_id>")
def consultar_endereco(endereco_id):
    """
    Consulta um endereço cadastrado.
    ---
    tags:
      - Endereços
    parameters:
      - name: endereco_id
        in: path
        type: integer
        required: true
        description: ID do endereço
        example: 2
    responses:
      200:
        description: Endereço encontrado
      404:
        description: Endereço não encontrado
      500:
        description: Erro interno no banco de dados
    """

    conexao = None

    try:
        conexao = obter_conexao()

        with conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    cliente_id,
                    cep,
                    logradouro,
                    numero,
                    complemento,
                    bairro,
                    cidade,
                    uf
                FROM enderecos
                WHERE id = %s
                """,
                (endereco_id,)
            )

            endereco = cursor.fetchone()

        if not endereco:
            return jsonify({
                "erro": "Endereço não encontrado."
            }), 404

        return jsonify({
            "endereco": {
                "id": endereco[0],
                "cliente_id": endereco[1],
                "cep": endereco[2],
                "logradouro": endereco[3],
                "numero": endereco[4],
                "complemento": endereco[5],
                "bairro": endereco[6],
                "cidade": endereco[7],
                "uf": endereco[8]
            }
        }), 200

    except Exception:
        return jsonify({
            "erro": "Não foi possível consultar o endereço."
        }), 500

    finally:
        if conexao:
            conexao.close()


@logistica_bp.put("/enderecos/<int:endereco_id>")
def atualizar_endereco(endereco_id):
    """
    Atualiza um endereço cadastrado.
    ---
    tags:
      - Endereços
    consumes:
      - application/json
    parameters:
      - name: endereco_id
        in: path
        type: integer
        required: true
        description: ID do endereço
        example: 2
      - in: body
        name: endereco
        required: true
        schema:
          type: object
          required:
            - cliente_id
            - cep
            - logradouro
            - numero
            - bairro
            - cidade
            - uf
          properties:
            cliente_id:
              type: integer
              example: 1
            cep:
              type: string
              example: "01001000"
            logradouro:
              type: string
              example: "Praça da Sé"
            numero:
              type: string
              example: "200"
            complemento:
              type: string
              example: "Sala 2"
            bairro:
              type: string
              example: "Sé"
            cidade:
              type: string
              example: "São Paulo"
            uf:
              type: string
              example: "SP"
    responses:
      200:
        description: Endereço atualizado com sucesso
      400:
        description: Dados inválidos
      404:
        description: Endereço ou cliente não encontrado
      500:
        description: Erro interno no banco de dados
    """

    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({
            "erro": "O corpo da requisição deve possuir dados em JSON."
        }), 400

    campos_obrigatorios = [
        "cliente_id",
        "cep",
        "logradouro",
        "numero",
        "bairro",
        "cidade",
        "uf"
    ]

    campos_faltantes = [
        campo
        for campo in campos_obrigatorios
        if campo not in dados
        or dados[campo] is None
        or str(dados[campo]).strip() == ""
    ]

    if campos_faltantes:
        return jsonify({
            "erro": "Campos obrigatórios não informados.",
            "campos": campos_faltantes
        }), 400

    try:
        cliente_id = int(dados["cliente_id"])
    except (TypeError, ValueError):
        return jsonify({
            "erro": "cliente_id deve ser um número inteiro."
        }), 400

    cep = "".join(filter(str.isdigit, str(dados["cep"])))

    if len(cep) != 8:
        return jsonify({
            "erro": "O CEP deve possuir 8 dígitos."
        }), 400

    uf = str(dados["uf"]).strip().upper()

    if len(uf) != 2:
        return jsonify({
            "erro": "A UF deve possuir 2 caracteres."
        }), 400

    conexao = None

    try:
        conexao = obter_conexao()

        with conexao.cursor() as cursor:

            cursor.execute(
                "SELECT id FROM enderecos WHERE id = %s",
                (endereco_id,)
            )

            endereco = cursor.fetchone()

            if not endereco:
                return jsonify({
                    "erro": "Endereço não encontrado."
                }), 404

            cursor.execute(
                "SELECT id FROM clientes WHERE id = %s AND ativo = TRUE",
                (cliente_id,)
            )

            cliente = cursor.fetchone()

            if not cliente:
                return jsonify({
                    "erro": "Cliente não encontrado ou inativo."
                }), 404

            cursor.execute(
                """
                UPDATE enderecos
                SET
                    cliente_id = %s,
                    cep = %s,
                    logradouro = %s,
                    numero = %s,
                    complemento = %s,
                    bairro = %s,
                    cidade = %s,
                    uf = %s
                WHERE id = %s
                """,
                (
                    cliente_id,
                    cep,
                    str(dados["logradouro"]).strip(),
                    str(dados["numero"]).strip(),
                    (
                        str(dados["complemento"]).strip()
                        if dados.get("complemento") is not None
                        else None
                    ),
                    str(dados["bairro"]).strip(),
                    str(dados["cidade"]).strip(),
                    uf,
                    endereco_id
                )
            )

        conexao.commit()

        return jsonify({
            "mensagem": "Endereço atualizado com sucesso.",
            "endereco": {
                "id": endereco_id,
                "cliente_id": cliente_id,
                "cep": cep,
                "logradouro": str(dados["logradouro"]).strip(),
                "numero": str(dados["numero"]).strip(),
                "complemento": (
                    str(dados["complemento"]).strip()
                    if dados.get("complemento") is not None
                    else None
                ),
                "bairro": str(dados["bairro"]).strip(),
                "cidade": str(dados["cidade"]).strip(),
                "uf": uf
            }
        }), 200

    except Exception:
        if conexao:
            conexao.rollback()

        return jsonify({
            "erro": "Não foi possível atualizar o endereço."
        }), 500

    finally:
        if conexao:
            conexao.close()


@logistica_bp.delete("/enderecos/<int:endereco_id>")
def excluir_endereco(endereco_id):
    """
    Exclui um endereço cadastrado.
    ---
    tags:
      - Endereços
    parameters:
      - name: endereco_id
        in: path
        type: integer
        required: true
        description: ID do endereço
        example: 2
    responses:
      200:
        description: Endereço excluído com sucesso
      404:
        description: Endereço não encontrado
      409:
        description: Endereço não pode ser excluído porque está sendo utilizado
      500:
        description: Erro interno no banco de dados
    """

    conexao = None

    try:
        conexao = obter_conexao()

        with conexao.cursor() as cursor:

            cursor.execute(
                "SELECT id FROM enderecos WHERE id = %s",
                (endereco_id,)
            )

            endereco = cursor.fetchone()

            if not endereco:
                return jsonify({
                    "erro": "Endereço não encontrado."
                }), 404

            cursor.execute(
                """
                SELECT 1
                FROM pedidos
                WHERE endereco_entrega_id = %s
                LIMIT 1
                """,
                (endereco_id,)
            )

            utilizado = cursor.fetchone()

            if utilizado:
                return jsonify({
                    "erro": "Não é possível excluir o endereço porque ele está sendo utilizado por um pedido."
                }), 409

            cursor.execute(
                "DELETE FROM enderecos WHERE id = %s",
                (endereco_id,)
            )

        conexao.commit()

        return jsonify({
            "mensagem": "Endereço excluído com sucesso.",
            "endereco_id": endereco_id
        }), 200

    except Exception:
        if conexao:
            conexao.rollback()

        return jsonify({
            "erro": "Não foi possível excluir o endereço."
        }), 500

    finally:
        if conexao:
            conexao.close()