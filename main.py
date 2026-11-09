"""Execução da rede KNN e das buscas já implementadas."""

import argparse
from time import perf_counter

from buscas import bfs, dfs
from rede import gerar_knn


def main() -> None:
    parser = argparse.ArgumentParser(description="SCC0230 — buscas em rede KNN")
    parser.add_argument("--vertices", type=int, default=100)
    parser.add_argument("--vizinhos", type=int, default=3)
    parser.add_argument("--semente", type=int, default=13)
    parser.add_argument("--origem", type=int, default=0)
    parser.add_argument("--destino", type=int,
                        help="Índice do destino; padrão: último vértice.")
    parser.add_argument("--algoritmo", choices=("bfs", "dfs", "ambos"),
                        default="ambos")
    args = parser.parse_args()
    destino = args.vertices - 1 if args.destino is None else args.destino

    if args.vertices < 1:
        parser.error("O número de vértices deve ser positivo.")
    if not 0 <= args.vizinhos < args.vertices:
        parser.error("O número de vizinhos deve satisfazer 0 <= k < n.")
    if not 0 <= args.origem < args.vertices or not 0 <= destino < args.vertices:
        parser.error("Origem e destino devem ser índices válidos da rede.")

    inicio = perf_counter()
    rede = gerar_knn(args.vertices, args.vizinhos, args.semente)
    tempo_geracao = perf_counter() - inicio
    print(f"REDE=KNN VERTICES={args.vertices} K={args.vizinhos} "
          f"SEMENTE={args.semente} ARESTAS={rede.numero_arestas}")
    print(f"ORIGEM={args.origem} DESTINO={destino}")
    print(f"TEMPO_GERACAO_S={tempo_geracao:.6f}")

    algoritmos = {"bfs": bfs, "dfs": dfs}
    selecionados = algoritmos if args.algoritmo == "ambos" else [args.algoritmo]
    for nome in selecionados:
        inicio = perf_counter()
        resultado = algoritmos[nome](rede, args.origem, destino)
        tempo = perf_counter() - inicio
        print(f"\nALGORITMO={nome.upper()}")
        print(f"VERTICES_EXPLORADOS={len(resultado.ordem_exploracao)}")
        print(f"TEMPO_BUSCA_S={tempo:.6f}")
        if resultado.caminho:
            print("CAMINHO=" + " -> ".join(map(str, resultado.caminho)))
            print(f"DISTANCIA={resultado.distancia:.6f}")
        else:
            print("CAMINHO=INEXISTENTE")
            print("DISTANCIA=INDEFINIDA")


if __name__ == "__main__":
    main()
