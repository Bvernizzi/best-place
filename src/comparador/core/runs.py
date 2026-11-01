import psycopg


def ultimo_hash(conn: psycopg.Connection, source: str) -> str | None:
    """Return the hash of the latest successful load, if any."""
    linha = conn.execute(
        """
        SELECT payload_sha256
        FROM bronze.ingestion_runs
        WHERE source = %s
          AND status = 'success'
        ORDER BY started_at DESC
        LIMIT 1
        """,
        (source,),
    ).fetchone()
    return linha[0] if linha else None


def iniciar_run(conn: psycopg.Connection, source: str, source_url: str) -> int:
    """Create a run with status 'running' and return its id."""
    return conn.execute(
        """
        INSERT INTO bronze.ingestion_runs (source, source_url, status)
        VALUES (%s, %s, 'running')
        RETURNING run_id
        """,
        (source, source_url),
    ).fetchone()[0]


def finalizar_run(
    conn: psycopg.Connection,
    run_id: int,
    status: str,
    payload_sha256: str | None = None,
    row_count: int | None = None,
    error_message: str | None = None,
) -> None:
    """Record the final state of a run."""
    conn.execute(
        """
        UPDATE bronze.ingestion_runs
        SET status = %s,
            payload_sha256 = %s,
            row_count = %s,
            error_message = %s,
            finished_at = now()
        WHERE run_id = %s
        """,
        (status, payload_sha256, row_count, error_message, run_id),
    )
