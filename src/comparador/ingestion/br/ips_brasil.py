import csv
import io

import psycopg
from psycopg.types.json import Jsonb

from comparador.core.carga import executar_carga

SOURCE = "br.ips_brasil"
EDICAO = 2026
URL = (
    "https://ipsbrasil.org.br/explore/data/export"
    "?edition_id=8723347c-668a-4ab0-9af8-4b180315bdd8"
)
MINIMO_MUNICIPIOS = 5000


def ler_ips(conteudo: bytes, minimo: int = MINIMO_MUNICIPIOS) -> list[dict]:
    """Return the CSV rows as dicts keyed by column name."""
    texto = conteudo.decode("utf-8-sig")  # the file starts with a BOM
    linhas = list(csv.DictReader(io.StringIO(texto)))

    if len(linhas) < minimo:
        raise ValueError(f"Expected at least {minimo} records, got {len(linhas)}")

    if "Município" not in linhas[0] or "UF" not in linhas[0]:
        raise ValueError("Expected columns 'Município' and 'UF' in the IPS file")

    return linhas


def gravar_ips(conn: psycopg.Connection, run_id: int, registros: list[dict]) -> None:
    """Store each row as raw JSONB, numbered by its position in the file."""
    with conn.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO bronze.ips_brasil (run_id, edicao, linha, payload)
             VALUES (%s, %s, %s, %s)
             """,
            [
                (run_id, EDICAO, numero, Jsonb(r))
                for numero, r in enumerate(registros, start=1)
            ],
        )


def executar() -> str:
    """Load the IPS Brasil table."""
    return executar_carga(SOURCE, URL, ler_ips, gravar_ips)
