"""Buscas cega e informadas, sem bibliotecas de busca prontas."""

from collections import deque
from dataclasses import dataclass
from heapq import heappop, heappush
from math import hypot

from rede import Rede


@dataclass
class ResultadoBusca:
    caminho: list[int]
    distancia: float | None
    ordem_exploracao: list[int]
    # Pai de cada vértice alcançado; permite desenhar a árvore de exploração.
    pais: dict[int, int | None]


def _validar_vertices(rede: Rede, origem: int, destino: int) -> None:
    n = len(rede.pontos)
    if not 0 <= origem < n or not 0 <= destino < n:
        raise ValueError("Origem e destino devem ser índices válidos da rede.")


def _resultado(rede: Rede, pais: dict[int, int | None],
               ordem: list[int], destino: int) -> ResultadoBusca:
    if destino not in pais:
        return ResultadoBusca([], None, ordem, pais)

    caminho = []
    atual: int | None = destino
    while atual is not None:
        caminho.append(atual)
        atual = pais[atual]
    caminho.reverse()
    distancia = sum((rede.adjacencias[a][b]
                     for a, b in zip(caminho, caminho[1:])), 0.0)
    return ResultadoBusca(caminho, distancia, ordem, pais)


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


def _heuristica(rede: Rede, destino: int):
    """Distância euclidiana ao destino: admissível, pois cada peso é euclidiano."""
    xd, yd = rede.pontos[destino]
    return lambda v: hypot(rede.pontos[v][0] - xd, rede.pontos[v][1] - yd)


def _busca_prioridade(rede: Rede, origem: int, destino: int,
                      usar_custo: bool, usar_heuristica: bool) -> ResultadoBusca:
    """Base comum de Best-First (h), A* (g + h) e Dijkstra (g)."""
    _validar_vertices(rede, origem, destino)
    h = _heuristica(rede, destino) if usar_heuristica else (lambda _: 0.0)
    custo = {origem: 0.0}
    pais: dict[int, int | None] = {origem: None}
    fechados: set[int] = set()
    ordem = []
    # Empates resolvidos pelo índice do vértice, para resultados reproduzíveis.
    fronteira = [(h(origem), origem)]

    while fronteira:
        _, atual = heappop(fronteira)
        if atual in fechados:
            continue
        fechados.add(atual)
        ordem.append(atual)
        if atual == destino:
            break
        for vizinho, peso in rede.adjacencias[atual].items():
            if vizinho in fechados:
                continue
            novo_custo = custo[atual] + peso
            if usar_custo:
                if novo_custo >= custo.get(vizinho, float("inf")):
                    continue
            elif vizinho in pais:
                continue
            custo[vizinho] = novo_custo
            pais[vizinho] = atual
            prioridade = h(vizinho) + (novo_custo if usar_custo else 0.0)
            heappush(fronteira, (prioridade, vizinho))

    return _resultado(rede, pais, ordem, destino)


def best_first(rede: Rede, origem: int, destino: int) -> ResultadoBusca:
    return _busca_prioridade(rede, origem, destino, False, True)


def a_estrela(rede: Rede, origem: int, destino: int) -> ResultadoBusca:
    return _busca_prioridade(rede, origem, destino, True, True)


def dijkstra(rede: Rede, origem: int, destino: int) -> ResultadoBusca:
    return _busca_prioridade(rede, origem, destino, True, False)


def hill_climbing(rede: Rede, origem: int, destino: int) -> ResultadoBusca:
    """Move-se ao vizinho de menor h; para em mínimo local, sem backtracking."""
    _validar_vertices(rede, origem, destino)
    h = _heuristica(rede, destino)
    pais: dict[int, int | None] = {origem: None}
    ordem = [origem]
    atual = origem

    while atual != destino:
        vizinhos = rede.adjacencias[atual]
        if not vizinhos:
            break
        melhor = min(vizinhos, key=lambda v: (h(v), v))
        if h(melhor) >= h(atual):
            break
        pais[melhor] = atual
        ordem.append(melhor)
        atual = melhor

    return _resultado(rede, pais, ordem, destino)
