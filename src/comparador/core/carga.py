import hashlib
from collections.abc import Callable

import psycopg

from comparador.core.db import conectar
from comparador.core.http import baixar_bytes
from comparador.core.runs import finalizar_run, iniciar_run, ultimo_hash


def calcular_hash(conteudo: bytes) -> str:
    """Return the SHA-256 of the content, used to detect changes between loads."""
    return hashlib.sha256(conteudo).hexdigest()

def executar_carga(
    source: str,
    url: str,
    ler: Callable[[bytes], list[dict]],
    gravar: Callable[[psycopg.Connection, int, list[dict]], None],
) -> str:
    """Run one idempotent load and return its final status."""
    with conectar() as conn:
        run_id = iniciar_run(conn, source, url)
        conn.commit()  # keep the run record even if the load fails

        try:
            conteudo = baixar_bytes(url)
            hash_atual = calcular_hash(conteudo)

            if hash_atual == ultimo_hash(conn, source):
                finalizar_run(conn, run_id, "skipped", payload_sha256=hash_atual)
                conn.commit()
                return "skipped"

            registros = ler(conteudo)
            gravar(conn, run_id, registros)
            finalizar_run(
                conn,
                run_id,
                "success",
                payload_sha256=hash_atual,
                row_count=len(registros),
            )
            conn.commit()
            return "success"
        except Exception as erro:
            conn.rollback()
            finalizar_run(conn, run_id, "failed", error_message=str(erro))
            conn.commit()
            raise