with ultimas_cargas as (
    select source, max(run_id) as run_id
    from {{ source('bronze', 'ingestion_runs') }}
    where source in ('br.ibge_populacao_censo', 'br.ibge_populacao_estimativa')
      and status = 'success'
    group by source
)

select
    p.municipio_id,
    p.ano,
    (p.payload ->> 'V')::bigint as populacao,
    case c.source
        when 'br.ibge_populacao_censo' then 'censo'
        else 'estimativa'
    end as tipo,
    p.loaded_at
from {{ source('bronze', 'ibge_populacao') }} as p
inner join ultimas_cargas as c using (run_id)