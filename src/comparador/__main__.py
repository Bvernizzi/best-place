import argparse

from comparador.ingestion.br import ibge_municipios, ibge_populacao, ips_brasil

FONTES = {
    "br.ibge_municipios": ibge_municipios.executar,
    "br.ibge_populacao_censo": ibge_populacao.executar_censo,
    "br.ibge_populacao_estimativa": ibge_populacao.executar_estimativa,
    "br.ips_brasil": ips_brasil.executar,
}


def main() -> None:
    parser = argparse.ArgumentParser(prog="comparador")
    parser.add_argument("comando", choices=["ingest"])
    parser.add_argument("fonte", choices=sorted(FONTES))
    args = parser.parse_args()
    print(f"{args.fonte}: {FONTES[args.fonte]()}")


if __name__ == "__main__":
    main()
