import hashlib
import json

import psycopg
from psycopg.types.json import Jsonb

from comparador.core.db import conectar
from comparador.core.http import baixar_bytes
from comparador.core.runs import finalizar_run, iniciar_run, ultimo_hash

SOURCE = "br.ibge_municipios"
URL = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
MINIMO_MUNICIPIOS = 5000


def calcular_hash(conteudo: bytes) -> str:
    """Return the SHA-256 of the content, used to detect changes between loads."""
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


def executar() -> str:
    """Run the load and return its final status."""
    with conectar() as conn:
        run_id = iniciar_run(conn, SOURCE, URL)
        conn.commit()  # keep the run record even if the load fails

        try:
            conteudo = baixar_bytes(URL)
            hash_atual = calcular_hash(conteudo)

            if hash_atual == ultimo_hash(conn, SOURCE):
                finalizar_run(conn, run_id, "skipped", payload_sha256=hash_atual)
                conn.commit()
                return "skipped"

            municipios = ler_municipios(conteudo)
            gravar_municipios(conn, run_id, municipios)
            finalizar_run(
                conn,
                run_id,
                "success",
                payload_sha256=hash_atual,
                row_count=len(municipios),
            )
            conn.commit()
            return "success"

        except Exception as erro:
            conn.rollback()
            finalizar_run(conn, run_id, "failed", error_message=str(erro))
            conn.commit()
            raise
