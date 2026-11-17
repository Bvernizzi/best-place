# Best Place

A data pipeline that brings together public data on Brazilian municipalities
to build a quality-of-life ranking based on each person's priorities.

> **Work in progress.** Ingestion and the cleaned (silver) layer are working
> for three sources. The ranking criteria are defined; the gold layer, the
> ranking and the app are not built yet.

## Goal

Comparing cities is hard: the information is scattered, and what matters
differs from person to person. In this project, users will set a weight for
each criterion, such as safety, health, parks, beaches and airports, and get
a personalized ranking.

Project rules:

- Zero cost, using only free public data.
- The 7-digit IBGE municipality code is the common key across sources.
- All municipalities are loaded; filtering by population is the user's choice.
- Every indicator keeps its source, reference year and load date.
- Built to support other countries later, without mixing them in one ranking.

## Architecture

```text
Public sources -> Python -> bronze -> silver -> gold -> app
```

| Layer | Role | Status |
|---|---|---|
| Ingestion | Downloads data with retries and skips unchanged files | Working |
| Bronze | Stores data exactly as received, in JSONB | Working |
| Silver | Cleans and types the data with dbt, with tests | Working |
| Gold | Normalized indicators per municipality, ranking criteria | In progress |
| App | Streamlit with weight sliders and a map | Planned |

### Key decisions

- **Postgres with PostGIS:** free, runs locally, and handles the spatial
  queries needed for airports, parks and beaches.
- **Raw JSONB in bronze:** keeps the original data, so later layers can be
  rebuilt without downloading again.
- **Content hashing:** if a source has not changed, the run is recorded as
  `skipped` and nothing is duplicated.
- **Atomic loads:** a failed load is rolled back, but the run is still
  recorded as `failed`, so there is a history without partial data.
- **dbt for transformations:** models in version-controlled SQL, with data
  tests on keys, relationships and accepted values.
- **Long format for indicators:** one row per municipality and indicator, so
  a new indicator is a new row, not a schema change.
- **One schema per layer:** `bronze`, `silver` and `gold` are separate
  Postgres schemas, so permissions can be granted per layer (the app only
  needs to read `gold`). A dbt macro keeps the exact schema names instead of
  dbt's default `silver_gold`.
- **Criteria as configuration:** ranking criteria, default weights and the
  mapping from source indicators to criteria live in dbt seeds. Adding a
  source or a country means adding rows, not changing SQL.
- **No Airflow in the MVP:** with few sources, an orchestrator would add more
  complexity than value. Runs will use a Makefile or GitHub Actions.

## Ranking criteria

The first version uses the 12 components of IPS Brasil 2026, grouped into 7
criteria. Components are already on a 0-100 scale where higher is better.
Users can change every weight; these are only the defaults.

| Criterion | IPS components | Default weight |
|---|---|---|
| Safety | Personal Safety | 25 |
| Health | Nutrition and Basic Medical Care; Health and Wellness | 20 |
| Education | Access to Basic Knowledge; Access to Advanced Education | 15 |
| Infrastructure | Water and Sanitation; Shelter | 15 |
| Environment | Environmental Quality | 10 |
| Connectivity | Access to Information and Communications | 10 |
| Inclusion and rights | Personal Rights; Personal Freedom and Choice; Inclusiveness | 5 |

Planned rules for the gold layer and the ranking:

- **Min-max normalization within each country**, over all municipalities,
  before any population filter. Scores do not depend on which other cities
  the user selected, and countries are never compared directly.
- **The overall IPS becomes a data test.** It is the simple mean of the 12
  components (checked: maximum difference of 0.007 across 5,570
  municipalities), so it cannot validate the ranking. Instead, a test checks
  that this mean still matches, which catches errors in ingestion or name
  matching.
- **Missing data excludes, not redistributes:** a municipality without data
  for a weighted criterion is left out of the ranking, so missing data never
  improves a position.

## Status

| Source | Data | Status |
|---|---|---|
| IBGE Localidades | Municipality list | Done |
| IBGE SIDRA | Population (2022 Census and 2026 estimate) | Done |
| IPS Brasil 2026 | Social Progress Index, 76 indicators | Done |
| ANAC | Airports | Planned |
| OpenStreetMap | Parks and beaches | Planned |
| CNES/DataSUS | Health | Planned |

The municipal HDI (Atlas Brasil) is only available up to 2010, so it is
not used for now.

## How to run

**Requirements:** Git, Python 3.11+ and Docker Desktop. The commands below
are for PowerShell on Windows.

1. Clone the repository:

```powershell
git clone https://github.com/Bvernizzi/best-place.git
cd best-place
```

2. Create `.env` and change the example password:

```powershell
Copy-Item .env.example .env
```

3. Install the project:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

4. Start the database and wait until it is `healthy`:

```powershell
docker compose up -d
docker compose ps
```

5. Create the bronze tables:

```powershell
Get-ChildItem sql\bronze\*.sql | Sort-Object Name | ForEach-Object { Get-Content $_.FullName | docker compose exec -T postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1' }
```

6. Load the sources:

```powershell
python -m comparador ingest br.ibge_municipios
python -m comparador ingest br.ibge_populacao_censo
python -m comparador ingest br.ibge_populacao_estimativa
python -m comparador ingest br.ips_brasil
```

7. Load the seeds and build and test the dbt models:

```powershell
Get-Content .env | ForEach-Object { $k, $v = $_ -split '=', 2; Set-Item "env:$k" $v }
dbt build --project-dir dbt --profiles-dir dbt
```

8. Run the Python tests:

```powershell
pytest
```

## Data limitations

- **Different reference years:** each source has its own reference year, so
  the indicators do not describe the same moment.
- **Small towns:** a handful of events can produce very unstable rates.
- **New municipalities:** Boa Esperança do Norte (MT) was established in
  2025. It has no microregion in the IBGE API and does not appear in the
  2022 Census or in IPS Brasil 2026.
- **IPS has no IBGE codes:** rows are matched by normalized name and state.
  5,565 match automatically, and 5 spelling differences are mapped by hand in
  a dbt seed. A dbt test fails if any row is left unmatched.
- **IPS editions are not comparable:** IPS Brasil states that its 2024, 2025
  and 2026 editions use different methods, so they cannot form a time series.
- **Quality of life:** the ranking reflects the chosen indicators and
  weights, not the full experience of living in a city.

## Sources

| Source | URL | License | Checked |
|---|---|---|---|
| IBGE Localidades | [Municipalities API](https://servicodados.ibge.gov.br/api/v1/localidades/municipios) | Not stated for the API; IBGE credited as the source | 2026-10-31 |
| IBGE SIDRA | [Table 4714](https://apisidra.ibge.gov.br/values/t/4714/n6/all/v/93/p/2022) and [table 6579](https://apisidra.ibge.gov.br/values/t/6579/n6/all/v/9324/p/2026) | Not stated for the API; IBGE credited as the source | 2026-11-02 |
| IPS Brasil 2026 | [Data page](https://ipsbrasil.org.br/explore/data) | No open license; the site states "all rights reserved" | 2026-11-04 |

This repository does not redistribute raw data: the pipeline downloads it
from the official sources on each run.

## Glossary

Code and table names use Brazilian Portuguese terms from the domain.

| Term | Meaning |
|---|---|
| `municipio` | Municipality |
| `populacao` | Population |
| `censo` / `estimativa` | Census / estimate |
| `carga` | Data load |
| `edicao` | Edition (of a yearly index) |
| `criterio` | Ranking criterion |
| `peso_padrao` | Default weight |
| `indicador` | Indicator |
| `direcao` | Direction (`maior_melhor`: higher is better) |