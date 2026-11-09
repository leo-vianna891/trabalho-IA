# SCC0230 — Busca em redes KNN

Projeto da disciplina de Inteligência Artificial da USP, abordagem A, grupo 13.

## Executar

Requer Python 3.10 ou superior. Não há dependências externas.

```sh
python3 main.py
python3 main.py --vertices 500 --vizinhos 7 --origem 0 --destino 499 --semente 13
python3 main.py --vertices 2500 --vizinhos 11 --algoritmo bfs
```

No Windows, pode-se substituir `python3` por `py -3` ou `python`, conforme a instalação.
Os vértices são numerados de 0 a n−1. O destino padrão é o último vértice.
A saída informa o caminho completo, a soma dos pesos, os vértices explorados e
os tempos de geração e busca. Uma execução isolada não constitui uma média experimental.

## Arquivos

- `rede.py`: coordenadas, adjacências e geração KNN.
- `buscas.py`: BFS, DFS e resultado comum com caminho, distância e ordem de exploração.
- `main.py`: parâmetros e execução pelo terminal.
- `Trabalho_IA.pdf`: enunciado original.

## Convenções da rede

- Coordenadas sorteadas no intervalo [0, n], com gerador local e semente reproduzível.
- Cada vértice seleciona seus k vizinhos mais próximos. Empates usam o índice do vértice.
- Grafo não direcionado: basta uma das escolhas para criar a ligação nos dois sentidos.
- Pesos iguais à distância euclidiana; sem laços ou arestas duplicadas.
- A união das escolhas não garante grau médio exatamente k, diferentemente da afirmação
  do enunciado. Não removemos ligações para forçar esse grau.
- Não forçamos conectividade. Se não houver caminho, a busca informa isso explicitamente.
- Aceita n >= 1 e 0 <= k < n; k = 0 permite representar uma rede sem arestas.

A BFS minimiza o número de arestas, não a distância ponderada. A DFS é iterativa,
com o percurso de profundidade equivalente ao recursivo. Ambas usam a ordem de
inserção das adjacências e não prometem o menor custo geométrico.
A ordem de exploração inclui o destino quando encontrado; ela não é o caminho solução.

## Escopo atual

Implementados: geração KNN, BFS e DFS. O gerador calcula as distâncias aos demais
vértices e seleciona os k menores sem construir uma matriz de distâncias.

Próximos algoritmos: Best-First, A*, Hill Climbing sem backtracking e Dijkstra
(para cumprir a comparação pedida no enunciado).
Visualização, experimentos sistemáticos, relatório e slides ainda não estão implementados.

Sem suíte de testes automatizados, CI/CD ou infraestrutura adicional.
