import pytest

from comparador.ingestion.br.ips_brasil import ler_ips


def _csv(
    *linhas: str, cabecalho: str = "Município,UF,Índice de Progresso Social"
) -> bytes:
    return ("\ufeff" + "\n".join([cabecalho, *linhas])).encode("utf-8")


def test_le_csv_com_bom():
    linhas = ler_ips(_csv("Campinas,SP,68.10", "Açu,RN,55.00"), minimo=2)
    assert linhas[1]["Município"] == "Açu"
    assert linhas[0]["Índice de Progresso Social"] == "68.10"


def test_rejeita_quantidade_abaixo_do_minimo():
    with pytest.raises(ValueError):
        ler_ips(_csv("Campinas,SP,68.10"), minimo=2)


def test_rejeita_arquivo_sem_coluna_uf():
    with pytest.raises(ValueError):
        ler_ips(_csv("Campinas,68.10", cabecalho="Município,Índice"), minimo=1)
