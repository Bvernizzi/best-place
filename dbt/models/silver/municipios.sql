with ultima_carga as (
    select max(run_id) as run_id
    from {{ source('bronze', 'ingestion_runs') }}
    where source = 'br.ibge_municipios'
      and status = 'success'
),

uf as (
    select
        m.municipio_id,
        m.payload ->> 'nome' as nome,
        m.payload -> 'regiao-imediata' -> 'regiao-intermediaria' -> 'UF' as uf_json,
        m.loaded_at
    from {{ source('bronze', 'ibge_municipios') }} as m
    inner join ultima_carga using (run_id)
)

select
    municipio_id,
    nome,
    uf_json ->> 'sigla' as uf,
    uf_json -> 'regiao' ->> 'nome' as regiao,
    loaded_at
from uf