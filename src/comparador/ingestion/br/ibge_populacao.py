import json

import psycopg
from psycopg.types.json import Jsonb

from comparador.core.carga import executar_carga

SOURCE_CENSO = "br.ibge_populacao_censo"
URL_CENSO = "https://apisidra.ibge.gov.br/values/t/4714/n6/all/v/93/p/2022"
SOURCE_ESTIMATIVA = "br.ibge_populacao_estimativa"
URL_ESTIMATIVA = "https://apisidra.ibge.gov.br/values/t/6579/n6/all/v/9324/p/2026"
MINIMO_MUNICIPIOS = 5000


def ler_populacao(conteudo: bytes, minimo: int = MINIMO_MUNICIPIOS) -> list[dict]:
    """Return the SIDRA records, dropping the header row."""
    linhas = json.loads(conteudo)[1:]
    if len(linhas) < minimo:
        raise ValueError(f"Expected at least {minimo} records, got {len(linhas)}")

    for linha in linhas:
        if len(linha["D1C"]) != 7:
            raise ValueError(f"Expected 7 digits, got code: {linha['D1C']}")

        return linhas


def gravar_populacao(
    conn: psycopg.Connection, run_id: int, registros: list[dict]
) -> None:
    """Store each record as raw JSONB under the given run."""
    with conn.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO bronze.ibge_populacao (run_id, municipio_id, ano, payload)
            VALUES (%s, %s, %s, %s)
            """,
            [(run_id, int(r["D1C"]), int(r["D3C"]), Jsonb(r)) for r in registros],
        )


def executar_censo() -> str:
    """Load the 2022 Census population."""
    return executar_carga(SOURCE_CENSO, URL_CENSO, ler_populacao, gravar_populacao)


def executar_estimativa() -> str:
    """Load the 2026 population estimate."""
    return executar_carga(
        SOURCE_ESTIMATIVA, URL_ESTIMATIVA, ler_populacao, gravar_populacao
    )
