with componentes as (
    select nome_fonte
    from {{ ref('indicadores_catalogo') }}
    where fonte = 'IPS Brasil'
),

media as (
    select
        ii.municipio_id,
        avg(ii.valor) as valor_medio,
        count(ii.indicador) as qtd_indicadores
    from {{ ref('ips_indicadores') }} as ii
    join componentes as c
        on ii.indicador = c.nome_fonte
    group by ii.municipio_id
),

indice as (
    select municipio_id, valor
    from {{ ref('ips_indicadores') }}
    where indicador = 'Índice de Progresso Social'
)

select
    m.municipio_id,
    m.valor_medio,
    i.valor as indice,
    m.qtd_indicadores
from media as m
join indice as i
    on i.municipio_id = m.municipio_id
where m.qtd_indicadores <> 12
   or abs(m.valor_medio - i.valor) > 0.01