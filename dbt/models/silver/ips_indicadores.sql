with ultima_carga as (
    select max(run_id) as run_id
    from {{ source('bronze', 'ingestion_runs') }}
    where source = 'br.ips_brasil'
      and status = 'success'
),

ips as (
    select
        p.edicao,
        p.payload,
        p.payload ->> 'Município' as nome,
        p.payload ->> 'UF' as uf
    from {{ source('bronze', 'ips_brasil') }} as p
    inner join ultima_carga using (run_id)
),

municipios as (
    select
        municipio_id,
        uf,
        regexp_replace(lower(unaccent(nome)), '[^a-z0-9]', '', 'g') as chave
    from {{ ref('municipios') }}
),

ligados as (
    select
        i.edicao,
        i.payload,
        coalesce(c.municipio_id, m.municipio_id) as municipio_id
    from ips as i
    left join {{ ref('ips_correspondencia') }} as c
        on c.nome_ips = i.nome and c.uf = i.uf
    left join municipios as m
        on m.uf = i.uf
        and m.chave = regexp_replace(lower(unaccent(i.nome)), '[^a-z0-9]', '', 'g')
)

select
    l.municipio_id,
    l.edicao,
    e.indicador,
    nullif(e.valor, '')::numeric as valor
from ligados as l
cross join lateral jsonb_each_text(l.payload) as e (indicador, valor)
where e.indicador not in ('Município', 'UF')