import os

import psycopg
from dotenv import load_dotenv


def conectar() -> psycopg.Connection:
    """Open a connection using the settings from .env."""
    load_dotenv()
    return psycopg.connect(
        host="127.0.0.1",
        port=5432,
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )
