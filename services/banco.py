import os

import psycopg
from dotenv import load_dotenv


load_dotenv()


def obter_conexao():
    """
    Cria uma conexão com o banco PostgreSQL do LogControl.
    """

    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "logcontrol"),
        user=os.getenv("DB_USER", "logcontrol"),
        password=os.getenv("DB_PASSWORD", "logcontrol_dev")
    )