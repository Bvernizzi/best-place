import pytest

from comparador.core.db import conectar
from comparador.core.runs import finalizar_run, iniciar_run, ultimo_hash
from comparador.ingestion.br.ibge_municipios import gravar_municipios

SOURCE = "teste.integracao"


@pytest.fixture
def conn():
    conexao = conectar()
    yield conexao
    conexao.rollback()
    conexao.close()


def test_ultimo_hash_vazio_sem_cargas(conn):
    assert ultimo_hash(conn, SOURCE) is None


def test_ultimo_hash_ignora_carga_com_falha(conn):
    run_ok = iniciar_run(conn, SOURCE, "https://exemplo.test")
    finalizar_run(conn, run_ok, "success", payload_sha256="aaa", row_count=1)
    run_ruim = iniciar_run(conn, SOURCE, "https://exemplo.test")
    finalizar_run(conn, run_ruim, "failed", error_message="erro")
    assert ultimo_hash(conn, SOURCE) == "aaa"


def test_grava_municipio_como_jsonb(conn):
    run_id = iniciar_run(conn, SOURCE, "https://exemplo.test")
    gravar_municipios(conn, run_id, [{"id": 3509502, "nome": "Campinas"}])
    nome = conn.execute(
        "SELECT payload->>'nome' FROM bronze.ibge_municipios WHERE run_id = %s",
        (run_id,),
    ).fetchone()[0]
    assert nome == "Campinas"
