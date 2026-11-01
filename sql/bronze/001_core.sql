CREATE SCHEMA IF NOT EXISTS bronze;

CREATE TABLE IF NOT EXISTS bronze.ingestion_runs (
    run_id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source         text NOT NULL,
    source_url     text NOT NULL,
    status         text NOT NULL
                   CHECK (status IN ('running', 'success', 'failed', 'skipped')),
    payload_sha256 text,
    row_count      int,
    error_message  text,
    started_at     timestamptz NOT NULL DEFAULT now(),
    finished_at    timestamptz
);

COMMENT ON TABLE bronze.ingestion_runs IS 'One row per load execution, with source, status and payload hash.';

CREATE TABLE IF NOT EXISTS bronze.ibge_municipios (
    run_id          bigint NOT NULL REFERENCES bronze.ingestion_runs (run_id),
    municipio_id    int NOT NULL,
    payload         jsonb NOT NULL,
    loaded_at       timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (run_id, municipio_id)
);

COMMENT ON TABLE bronze.ibge_municipios IS 'Raw IBGE municipality records, as returned by the API, one version per load.';
