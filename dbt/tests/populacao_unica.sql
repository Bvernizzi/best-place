select municipio_id, tipo
from {{ ref('populacao') }}
group by municipio_id, tipo
having count(*) > 1