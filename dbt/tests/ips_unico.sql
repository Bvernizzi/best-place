select municipio_id, indicador
from {{ ref('ips_indicadores') }}
group by municipio_id, indicador
having count(*) > 1