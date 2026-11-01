import hashlib
import json

SOURCE = "br.ibge_municipios"
URL = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
MINIMO_MUNICIPIOS = 5000

# Change detection
# ---- Return the SHA-256 of the content, used to detect changes between loads.
def calcular_hash(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()


def ler_municipios(conteudo: bytes, minimo: int = MINIMO_MUNICIPIOS) -> list[dict]:
    municipios = json.loads(conteudo)
    if len(municipios) < minimo:
        raise ValueError(f"Expected at least {minimo} records, got {len(municipios)}")

    for municipio in municipios:
        if len(str(municipio["id"])) != 7:
            raise ValueError(f"Expected 7 digits, got ID: {municipio['id']}")
    
    return municipios