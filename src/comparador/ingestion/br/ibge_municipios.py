import hashlib
import json

import psycopg
from psycopg.types.json import Jsonb

SOURCE = "br.ibge_municipios"
URL = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
MINIMO_MUNICIPIOS = 5000

# Change detection
""" Return the SHA-256 of the content, used to detect changes between loads."""


def calcular_hash(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()


def ler_municipios(conteudo: bytes, minimo: int = MINIMO_MUNICIPIOS) -> list[dict]:
    municipios = json.loads(conteudo)
    if len(municipios) < minimo:
        raise ValueError(f"Expected at least {minimo} records, got {len(municipios)}")

    for municipio in municipios:
        if len(str(municipio["id"])) != 7:
            raise ValueError(f"Expected 7 digits, got ID: {municipio['id']}")

    return municipios


def gravar_municipios(
    conn: psycopg.Connection, run_id: int, municipios: list[dict]
) -> None:
    """Store each municipality as raw JSONB under the given run."""
    with conn.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO bronze.ibge_municipios (run_id, municipio_id, payload)
            VALUES (%s, %s, %s)
            """,
            [(run_id, m["id"], Jsonb(m)) for m in municipios],
        )
