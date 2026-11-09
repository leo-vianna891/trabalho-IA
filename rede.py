"""Geração de uma rede KNN geométrica não direcionada."""

from dataclasses import dataclass
from heapq import nsmallest
from math import hypot
from random import Random


@dataclass
class Rede:
    pontos: list[tuple[float, float]]
    adjacencias: list[dict[int, float]]

    @property
    def numero_arestas(self) -> int:
        return sum(len(vizinhos) for vizinhos in self.adjacencias) // 2


def gerar_knn(n: int, k: int, semente: int = 13) -> Rede:
    if n < 1:
        raise ValueError("O número de vértices deve ser positivo.")
    if not 0 <= k < n:
        raise ValueError("O número de vizinhos deve satisfazer 0 <= k < n.")

    aleatorio = Random(semente)
    pontos = [(aleatorio.uniform(0, n), aleatorio.uniform(0, n))
              for _ in range(n)]
    adjacencias: list[dict[int, float]] = [{} for _ in range(n)]

    for origem, (x, y) in enumerate(pontos):
        def proximidade(destino: int) -> tuple[float, int]:
            dx = x - pontos[destino][0]
            dy = y - pontos[destino][1]
            return dx * dx + dy * dy, destino

        candidatos = (destino for destino in range(n) if destino != origem)
        vizinhos = nsmallest(k, candidatos, key=proximidade)
        for destino in vizinhos:
            if destino not in adjacencias[origem]:
                peso = hypot(x - pontos[destino][0], y - pontos[destino][1])
                adjacencias[origem][destino] = peso
                adjacencias[destino][origem] = peso

    return Rede(pontos, adjacencias)
