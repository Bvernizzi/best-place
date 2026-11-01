import json
from pathlib import Path

import pytest

from comparador.ingestion.br.ibge_municipios import calcular_hash, ler_municipios

AMOSTRA = Path(__file__).parents[1] / "fixtures" / "ibge_municipios_amostra.json"


def test_hash_e_estavel_e_muda_com_o_conteudo():
    assert calcular_hash(b"abc") == calcular_hash(b"abc")
    assert calcular_hash(b"abc") != calcular_hash(b"abd")
    assert len(calcular_hash(b"abc")) == 64


def test_aceita_municipio_sem_microrregiao():
    municipios = ler_municipios(AMOSTRA.read_bytes(), minimo=2)
    assert municipios[1]["microrregiao"] is None


def test_rejeita_quantidade_abaixo_do_minimo():
    with pytest.raises(ValueError):
        ler_municipios(AMOSTRA.read_bytes(), minimo=3)


def test_rejeita_id_invalido():
    conteudo = json.dumps([{"id": 123, "nome": "Teste"}]).encode()
    with pytest.raises(ValueError):
        ler_municipios(conteudo, minimo=1)
