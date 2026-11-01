# Teste se está baixando uma URL

import httpx
import pytest
import respx

from comparador.core.http import baixar_bytes

URL = "https://exemplo.test/dados"


@respx.mock
def test_retorna_bytes_quando_responde_200():
    respx.get(URL).mock(return_value=httpx.Response(200, content=b"ok"))
    assert baixar_bytes(URL) == b"ok"


@respx.mock
def test_tenta_de_novo_depois_de_503():
    rota = respx.get(URL).mock(
        side_effect=[httpx.Response(503), httpx.Response(200, content=b"ok")]
    )
    assert baixar_bytes(URL) == b"ok"
    assert rota.call_count == 2


@respx.mock
def test_nao_tenta_de_novo_em_404():
    rota = respx.get(URL).mock(return_value=httpx.Response(404))
    with pytest.raises(httpx.HTTPStatusError):
        baixar_bytes(URL)
    assert rota.call_count == 1
