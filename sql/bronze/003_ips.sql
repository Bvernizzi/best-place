CREATE EXTENSION IF NOT EXISTS unaccent;

CREATE TABLE IF NOT EXISTS bronze.ips_brasil (
    run_id          bigint NOT NULL REFERENCES bronze.ingestion_runs (run_id),
    edicao          int NOT NULL,
    linha           int NOT NULL,
    payload         jsonb NOT NULL,
    loaded_at       timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (run_id, linha)
);

COMMENT ON TABLE bronze.ips_brasil IS 'Raw IPS Brasil CSV rows, one version per load, identified by run.';