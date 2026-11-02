import json

import pytest

from comparador.ingestion.br.ibge_populacao import ler_populacao


def _sidra(*codigos: str) -> bytes:
    cabecalho = {"V": "Valor", "D1C": "Município (Código)", "D3C": "Ano (Código)"}
    linhas = [{"V": "100", "D1C": codigo, "D3C": "2022"} for codigo in codigos]
    return json.dumps([cabecalho, *linhas]).encode()


def test_remove_cabecalho():
    assert len(ler_populacao(_sidra("3509502", "3550308"), minimo=2)) == 2


def test_rejeita_quantidade_abaixo_do_minimo():
    with pytest.raises(ValueError):
        ler_populacao(_sidra("3509502"), minimo=2)


def test_rejeita_codigo_invalido():
    with pytest.raises(ValueError):
        ler_populacao(_sidra("123"), minimo=1)
