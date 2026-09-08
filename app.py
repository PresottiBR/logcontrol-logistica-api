from flask import Flask, jsonify
from flasgger import Swagger

from routes.logistica import logistica_bp


app = Flask(__name__)
swagger = Swagger(app)


app.register_blueprint(logistica_bp)


@app.get("/")
def home():
    """
    Verifica o status da API de Logística.
    ---
    tags:
      - Sistema
    responses:
      200:
        description: API funcionando corretamente
    """
    return jsonify({
        "sistema": "LogControl - API de Logística",
        "status": "online",
        "mensagem": "API de Logística funcionando corretamente"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5002)