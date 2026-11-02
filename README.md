# Best Place

Pipeline de dados que reúne fontes públicas sobre os municípios brasileiros
para gerar um ranking de qualidade de vida conforme as prioridades de cada pessoa.

> **Projeto em desenvolvimento.** A carga da lista de municípios já funciona.
> Indicadores, ranking e app ainda não foram construídos.

## Objetivo

Comparar cidades é difícil porque a informação está espalhada e o que importa
muda de pessoa para pessoa. Neste projeto, o usuário definirá o peso de cada
critério, como segurança, saúde, parques, praia e aeroporto, e receberá um
ranking personalizado.

Regras do projeto:

- Custo zero, com fontes públicas e gratuitas.
- Código IBGE de 7 dígitos como chave comum entre as fontes.
- Carga de todos os municípios; o filtro por população é escolha do usuário.
- Cada indicador guarda fonte, ano de referência e data de carga.
- Arquitetura preparada para outros países, sem misturá-los em um ranking único.

## Arquitetura

```text
Fontes públicas -> Python -> bronze -> silver -> gold -> app
```

| Camada | Função | Situação |
|---|---|---|
| Ingestão | Baixa os dados com retry e evita cargas repetidas | Em andamento |
| Bronze | Guarda os dados como vieram da fonte, em JSONB | Em andamento |
| Silver | Limpa e padroniza os dados com dbt | Planejada |
| Gold | Reúne os indicadores por município | Planejada |
| App | Streamlit com sliders de peso e mapa | Planejada |

### Principais decisões

- **Postgres com PostGIS:** gratuito, roda localmente e faz as consultas
  geográficas necessárias para aeroportos, parques e praias.
- **Bronze em JSONB:** preserva o dado original e permite reprocessar as
  próximas camadas sem baixar tudo de novo.
- **Hash do conteúdo:** se a fonte não mudou, a execução é registrada como
  `skipped` e nada é duplicado.
- **dbt na transformação:** mantém os modelos em SQL, com testes e documentação.
- **Sem Airflow no MVP:** com poucas fontes, um orquestrador traria mais
  complexidade do que benefício. A execução será por Makefile ou GitHub Actions.

## Status

| Fonte | Dado | Situação |
|---|---|---|
| IBGE Localidades | Lista de municípios | Concluída |
| IBGE SIDRA | População | Próxima |
| Atlas Brasil e IPS Brasil | IDHM e progresso social | Planejada |
| ANAC | Aeroportos | Planejada |
| OpenStreetMap | Parques e praias | Planejada |
| CNES/DataSUS | Saúde | Planejada |
| Segurança | A definir | Planejada |

## Como rodar

**Requisitos:** Git, Python 3.11+ e Docker Desktop. Os comandos abaixo são para
PowerShell, no Windows.

1. Clone o repositório:

```powershell
git clone https://github.com/Bvernizzi/best-place.git
cd best-place
```

2. Crie o `.env` e troque a senha de exemplo:

```powershell
Copy-Item .env.example .env
```

3. Instale o projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

4. Suba o banco e aguarde o estado `healthy`:

```powershell
docker compose up -d
docker compose ps
```

5. Crie as tabelas:

```powershell
Get-Content sql\bronze\001_core.sql | docker compose exec -T postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1'
```

6. Faça a primeira carga:

```powershell
python -m comparador ingest br.ibge_municipios
```

7. Rode os testes:

```powershell
pytest
```

## Limitações dos dados

- **Datas diferentes:** cada fonte tem seu próprio ano de referência, então os
  indicadores não descrevem o mesmo momento.
- **Cidades pequenas:** poucas ocorrências podem gerar taxas muito instáveis.
- **Municípios novos:** Boa Esperança do Norte (MT) foi instalado em 2025, não tem microrregião na API do IBGE e não aparece na tabela do Censo 2022.  tem microrregião na API do IBGE. A cobertura em bases mais antigas precisa ser verificada.
- **Segurança:** dados recentes podem ser revisados, e o atraso no envio por um
  estado pode distorcer comparações.
- **Qualidade de vida:** o ranking reflete os indicadores e pesos escolhidos, não
  uma medida completa da experiência de morar em uma cidade.

## Fontes

| Fonte | URL | Licença | Verificação |
|---|---|---|---|
| IBGE Localidades | [API de municípios](https://servicodados.ibge.gov.br/api/v1/localidades/municipios) | Não confirmada para a API; citar o IBGE como fonte | 31/10/2026 |

As demais fontes entram nesta tabela depois de terem URL, formato e licença
confirmados. Este repositório não redistribui dados brutos.