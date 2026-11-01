# Baixa uma URL e tenta de novo em falhas temporárias

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)


def _deve_tentar_de_novo(erro: BaseException) -> bool:
    if isinstance(erro, httpx.TransportError):
        return True
    if isinstance(erro, httpx.HTTPStatusError):
        status = erro.response.status_code
        return status == 429 or 500 <= status <= 599
    return False


@retry(
    retry=retry_if_exception(_deve_tentar_de_novo),
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1, max=30),
    reraise=True,
)
def baixar_bytes(url: str, timeout: float = 60.0) -> bytes:
    resposta = httpx.get(url, timeout=timeout, follow_redirects=True)
    resposta.raise_for_status()
    return resposta.content
