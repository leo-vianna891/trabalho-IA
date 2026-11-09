"""Buscas em largura e profundidade, sem bibliotecas de busca prontas."""

from collections import deque
from dataclasses import dataclass

from rede import Rede


@dataclass
class ResultadoBusca:
    caminho: list[int]
    distancia: float | None
    ordem_exploracao: list[int]


def _validar_vertices(rede: Rede, origem: int, destino: int) -> None:
    n = len(rede.pontos)
    if not 0 <= origem < n or not 0 <= destino < n:
        raise ValueError("Origem e destino devem ser índices válidos da rede.")


def _resultado(rede: Rede, pais: dict[int, int | None],
               ordem: list[int], destino: int) -> ResultadoBusca:
    if destino not in pais:
        return ResultadoBusca([], None, ordem)

    caminho = []
    atual: int | None = destino
    while atual is not None:
        caminho.append(atual)
        atual = pais[atual]
    caminho.reverse()
    distancia = sum((rede.adjacencias[a][b]
                     for a, b in zip(caminho, caminho[1:])), 0.0)
    return ResultadoBusca(caminho, distancia, ordem)


def bfs(rede: Rede, origem: int, destino: int) -> ResultadoBusca:
    _validar_vertices(rede, origem, destino)
    fila = deque([origem])
    pais: dict[int, int | None] = {origem: None}
    ordem = []

    while fila:
        atual = fila.popleft()
        ordem.append(atual)
        if atual == destino:
            break
        for vizinho in rede.adjacencias[atual]:
            if vizinho not in pais:
                pais[vizinho] = atual
                fila.append(vizinho)

    return _resultado(rede, pais, ordem, destino)


def dfs(rede: Rede, origem: int, destino: int) -> ResultadoBusca:
    _validar_vertices(rede, origem, destino)
    pais: dict[int, int | None] = {origem: None}
    ordem = [origem]
    pilha = [(origem, iter(rede.adjacencias[origem]))]

    # Iteradores preservam o percurso recursivo, sem limite de recursão.
    while pilha and ordem[-1] != destino:
        _, vizinhos = pilha[-1]
        vizinho = next(vizinhos, None)
        if vizinho is None:
            pilha.pop()
        elif vizinho not in pais:
            pais[vizinho] = pilha[-1][0]
            ordem.append(vizinho)
            pilha.append((vizinho, iter(rede.adjacencias[vizinho])))

    return _resultado(rede, pais, ordem, destino)
