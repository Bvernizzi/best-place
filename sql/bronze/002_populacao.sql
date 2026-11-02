CREATE TABLE IF NOT EXISTS bronze.ibge_populacao (
    run_id          bigint NOT NULL REFERENCES bronze.ingestion_runs (run_id),
    municipio_id    int NOT NULL,
    ano             int NOT NULL,
    payload         jsonb NOT NULL,
    loaded_at       timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (run_id, municipio_id)
);

COMMENT ON TABLE bronze.ibge_populacao IS 'Raw SIDRA population records, one version per load, identified by run.';