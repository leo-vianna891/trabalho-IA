"""Interface gráfica (tkinter) para gerar a rede KNN e animar as buscas."""

import tkinter as tk
from random import Random
from time import perf_counter
from tkinter import ttk

from buscas import (ResultadoBusca, a_estrela, best_first, bfs, dfs, dijkstra,
                    hill_climbing)
from rede import Rede, gerar_knn

ALGORITMOS = {
    "Busca em largura (BFS)": bfs,
    "Busca em profundidade (DFS)": dfs,
    "Best-First": best_first,
    "A*": a_estrela,
    "Hill Climbing": hill_climbing,
    "Dijkstra": dijkstra,
}

# Níveis de velocidade: (atraso entre quadros em ms, vértices por quadro).
VELOCIDADES = [(400, 1), (200, 1), (100, 1), (50, 1), (25, 1),
               (10, 1), (4, 1), (1, 2), (1, 6), (1, 20)]

COR_FUNDO = "#ffffff"
COR_ARESTA = "#d9dde3"
COR_VERTICE = "#9aa3ad"
COR_VISITADO = "#4a90d9"
COR_ATUAL = "#f5a623"
COR_CAMINHO = "#d0021b"
COR_ORIGEM = "#2e9e44"
COR_DESTINO = "#8e44ad"
MARGEM = 20


class Interface:
    def __init__(self, raiz: tk.Tk) -> None:
        self.raiz = raiz
        raiz.title("SCC0230 — Buscas em rede KNN")
        raiz.geometry("1200x800")
        raiz.minsize(900, 600)

        self.vertices = tk.IntVar(value=300)
        self.vizinhos = tk.IntVar(value=5)
        self.semente = tk.IntVar(value=13)
        self.algoritmo = tk.StringVar(value="A*")
        self.velocidade = tk.IntVar(value=5)
        self.status = tk.StringVar()
        self.info = tk.StringVar()

        self.aleatorio = Random()
        self.rede: Rede | None = None
        self.origem = 0
        self.destino = 0
        self.resultado: ResultadoBusca | None = None
        self.tempo_busca = 0.0
        self.indice = 0          # quantos vértices da exploração já foram exibidos
        self.finalizado = False
        self.animacao: str | None = None
        self.redesenho: str | None = None
        self.ids_arestas: dict[tuple[int, int], int] = {}
        self.ids_vertices: list[int] = []

        self._montar_controles()
        self.canvas = tk.Canvas(raiz, bg=COR_FUNDO, highlightthickness=0)
        self.canvas.pack(side="right", fill="both", expand=True)
        self.canvas.bind("<Configure>", self._agendar_redesenho)

        self.gerar_rede()

    # ----------------------------------------------------------- controles
    def _montar_controles(self) -> None:
        painel = ttk.Frame(self.raiz, padding=12)
        painel.pack(side="left", fill="y")

        rede = ttk.LabelFrame(painel, text="Rede KNN", padding=8)
        rede.pack(fill="x")
        self._campo(rede, "Vértices (n)", self.vertices, 10, 2500, 50)
        self._campo(rede, "Vizinhos k (densidade)", self.vizinhos, 1, 30, 1)
        self._campo(rede, "Semente", self.semente, 0, 10**9, 1)
        self.botao_rede = ttk.Button(rede, text="Gerar rede",
                                     command=self.gerar_rede)
        self.botao_rede.pack(fill="x", pady=(6, 2))
        self.botao_nova = ttk.Button(rede, text="Nova disposição aleatória",
                                     command=self.nova_disposicao)
        self.botao_nova.pack(fill="x", pady=2)
        ttk.Label(rede, text="Para visualizar, prefira 100–500 vértices.",
                  foreground="#666").pack(anchor="w", pady=(4, 0))

        par = ttk.LabelFrame(painel, text="Origem e destino", padding=8)
        par.pack(fill="x", pady=10)
        self.rotulo_par = ttk.Label(par, text="")
        self.rotulo_par.pack(anchor="w")
        self.botao_par = ttk.Button(par, text="Sortear origem e destino",
                                    command=self.sortear_par)
        self.botao_par.pack(fill="x", pady=(6, 0))

        busca = ttk.LabelFrame(painel, text="Busca", padding=8)
        busca.pack(fill="x")
        self.combo = ttk.Combobox(busca, textvariable=self.algoritmo,
                                  values=list(ALGORITMOS), state="readonly")
        self.combo.pack(fill="x")
        ttk.Label(busca, text="Velocidade da animação").pack(anchor="w",
                                                             pady=(8, 0))
        ttk.Scale(busca, from_=1, to=len(VELOCIDADES), orient="horizontal",
                  command=lambda v: self.velocidade.set(round(float(v))),
                  value=self.velocidade.get()).pack(fill="x")
        self.botao_iniciar = ttk.Button(busca, text="Iniciar busca",
                                        command=self.iniciar_busca)
        self.botao_iniciar.pack(fill="x", pady=(8, 2))
        self.botao_finalizar = ttk.Button(busca, text="Finalizar",
                                          command=self.finalizar,
                                          state="disabled")
        self.botao_finalizar.pack(fill="x", pady=2)

        legenda = ttk.LabelFrame(painel, text="Legenda", padding=8)
        legenda.pack(fill="x", side="bottom")
        for cor, texto in ((COR_ORIGEM, "Origem"), (COR_DESTINO, "Destino"),
                           (COR_ATUAL, "Vértice sendo expandido"),
                           (COR_VISITADO, "Visitado / aresta explorada"),
                           (COR_CAMINHO, "Caminho encontrado")):
            linha = ttk.Frame(legenda)
            linha.pack(anchor="w")
            amostra = tk.Canvas(linha, width=14, height=14,
                                highlightthickness=0)
            amostra.create_oval(2, 2, 12, 12, fill=cor, outline=cor)
            amostra.pack(side="left")
            ttk.Label(linha, text=texto).pack(side="left", padx=4)

        ttk.Label(painel, textvariable=self.status, wraplength=240,
                  font=("TkDefaultFont", 10, "bold")).pack(anchor="w",
                                                           pady=(10, 2))
        ttk.Label(painel, textvariable=self.info, wraplength=240,
                  justify="left").pack(anchor="w")

    @staticmethod
    def _campo(pai, texto: str, variavel: tk.IntVar,
               minimo: int, maximo: int, passo: int) -> None:
        ttk.Label(pai, text=texto).pack(anchor="w")
        ttk.Spinbox(pai, from_=minimo, to=maximo, increment=passo,
                    textvariable=variavel, width=10).pack(fill="x",
                                                          pady=(0, 4))

    def _habilitar(self, ativo: bool) -> None:
        estado = "normal" if ativo else "disabled"
        for botao in (self.botao_rede, self.botao_nova, self.botao_par,
                      self.botao_iniciar):
            botao.configure(state=estado)
        self.combo.configure(state="readonly" if ativo else "disabled")
        self.botao_finalizar.configure(state="disabled" if ativo else "normal")

    # --------------------------------------------------------------- rede
    def _ler_parametros(self) -> tuple[int, int, int] | None:
        try:
            n, k, semente = (self.vertices.get(), self.vizinhos.get(),
                             self.semente.get())
        except tk.TclError:
            self.status.set("Parâmetros devem ser números inteiros.")
            return None
        if not 2 <= n <= 2500:
            self.status.set("Use entre 2 e 2500 vértices.")
            return None
        if not 1 <= k < n:
            self.status.set("O número de vizinhos deve satisfazer 1 <= k < n.")
            return None
        return n, k, semente

    def gerar_rede(self) -> None:
        parametros = self._ler_parametros()
        if parametros is None:
            return
        n, k, semente = parametros
        self.status.set("Gerando rede...")
        self.raiz.update_idletasks()
        inicio = perf_counter()
        self.rede = gerar_knn(n, k, semente)
        tempo = perf_counter() - inicio
        self.status.set(f"Rede gerada: {n} vértices, "
                        f"{self.rede.numero_arestas} arestas ({tempo:.2f} s).")
        self.info.set("")
        self.sortear_par()

    def nova_disposicao(self) -> None:
        self.semente.set(self.aleatorio.randrange(10**6))
        self.gerar_rede()

    def sortear_par(self) -> None:
        if self.rede is None:
            return
        n = len(self.rede.pontos)
        self.origem, self.destino = self.aleatorio.sample(range(n), 2)
        self.rotulo_par.configure(
            text=f"Origem: {self.origem}    Destino: {self.destino}")
        self._limpar_busca()
        self.desenhar()

    # ------------------------------------------------------------- desenho
    def _agendar_redesenho(self, _evento=None) -> None:
        if self.redesenho is not None:
            self.raiz.after_cancel(self.redesenho)
        self.redesenho = self.raiz.after(120, self.desenhar)

    def _tela(self, vertice: int) -> tuple[float, float]:
        x, y = self.rede.pontos[vertice]
        return MARGEM + x * self.escala, MARGEM + y * self.escala

    def desenhar(self) -> None:
        self.redesenho = None
        if self.rede is None:
            return
        largura = self.canvas.winfo_width()
        altura = self.canvas.winfo_height()
        n = len(self.rede.pontos)
        self.escala = max(min(largura - 2 * MARGEM, altura - 2 * MARGEM), 1) / n
        self.raio = 3.5 if n <= 300 else 2.5 if n <= 1000 else 1.5

        self.canvas.delete("all")
        self.ids_arestas.clear()
        for a, vizinhos in enumerate(self.rede.adjacencias):
            xa, ya = self._tela(a)
            for b in vizinhos:
                if a < b:
                    xb, yb = self._tela(b)
                    self.ids_arestas[(a, b)] = self.canvas.create_line(
                        xa, ya, xb, yb, fill=COR_ARESTA, tags="aresta")
        r = self.raio
        self.ids_vertices = []
        for v in range(n):
            x, y = self._tela(v)
            self.ids_vertices.append(self.canvas.create_oval(
                x - r, y - r, x + r, y + r, fill=COR_VERTICE, outline="",
                tags="vertice"))
        self._aplicar_estado()

    def _aresta(self, a: int, b: int) -> int | None:
        return self.ids_arestas.get((min(a, b), max(a, b)))

    def _pintar_vertice(self, v: int, cor: str, escala: float = 1.0) -> None:
        r = self.raio * escala
        x, y = self._tela(v)
        item = self.ids_vertices[v]
        self.canvas.coords(item, x - r, y - r, x + r, y + r)
        self.canvas.itemconfigure(item, fill=cor)
        self.canvas.tag_raise(item)

    def _pintar_aresta(self, a: int, b: int, cor: str, largura: float) -> None:
        item = self._aresta(a, b)
        if item is not None:
            self.canvas.itemconfigure(item, fill=cor, width=largura)
            self.canvas.tag_raise(item, "aresta")

    def _marcar_visitado(self, v: int) -> None:
        pai = self.resultado.pais.get(v)
        if pai is not None:
            self._pintar_aresta(pai, v, COR_VISITADO, 1.8)
        self._pintar_vertice(v, COR_VISITADO, 1.2)

    def _destacar_extremos(self) -> None:
        # Tamanho mínimo para que origem e destino fiquem visíveis em redes grandes.
        escala = max(2.2, 6 / self.raio)
        self._pintar_vertice(self.origem, COR_ORIGEM, escala)
        self._pintar_vertice(self.destino, COR_DESTINO, escala)

    def _aplicar_estado(self) -> None:
        """Repinta a busca até o índice atual (usado também após redimensionar)."""
        if self.resultado is not None:
            for v in self.resultado.ordem_exploracao[:self.indice]:
                self._marcar_visitado(v)
            if self.finalizado and self._encontrou():
                caminho = self.resultado.caminho
                for a, b in zip(caminho, caminho[1:]):
                    self._pintar_aresta(a, b, COR_CAMINHO, 3.5)
                for v in caminho:
                    self._pintar_vertice(v, COR_CAMINHO, 1.5)
            elif not self.finalizado and self.indice:
                atual = self.resultado.ordem_exploracao[self.indice - 1]
                self._pintar_vertice(atual, COR_ATUAL, 2.0)
        self.canvas.tag_raise("vertice")
        self._destacar_extremos()

    # -------------------------------------------------------------- busca
    def _encontrou(self) -> bool:
        """O caminho só é exibido se a animação chegou ao destino."""
        ordem = self.resultado.ordem_exploracao
        return bool(self.resultado.caminho) and self.indice >= len(ordem)

    def _limpar_busca(self) -> None:
        if self.animacao is not None:
            self.raiz.after_cancel(self.animacao)
            self.animacao = None
        self.resultado = None
        self.indice = 0
        self.finalizado = False
        self._habilitar(True)

    def iniciar_busca(self) -> None:
        if self.rede is None:
            return
        self._limpar_busca()
        funcao = ALGORITMOS[self.algoritmo.get()]
        inicio = perf_counter()
        self.resultado = funcao(self.rede, self.origem, self.destino)
        self.tempo_busca = perf_counter() - inicio
        self.desenhar()
        self._habilitar(False)
        self.status.set(f"Executando {self.algoritmo.get()}...")
        self._passo()

    def _passo(self) -> None:
        ordem = self.resultado.ordem_exploracao
        atraso, quantidade = VELOCIDADES[self.velocidade.get() - 1]
        if self.indice:
            self._marcar_visitado(ordem[self.indice - 1])
        for v in ordem[self.indice:self.indice + quantidade]:
            self._marcar_visitado(v)
        self.indice = min(self.indice + quantidade, len(ordem))
        self._pintar_vertice(ordem[self.indice - 1], COR_ATUAL, 2.0)
        self._destacar_extremos()
        self.info.set(f"Vértices explorados: {self.indice} de {len(ordem)}")
        if self.indice >= len(ordem):
            self.animacao = None
            self.finalizar()
        else:
            self.animacao = self.raiz.after(atraso, self._passo)

    def finalizar(self) -> None:
        if self.resultado is None or self.finalizado:
            return
        if self.animacao is not None:
            self.raiz.after_cancel(self.animacao)
            self.animacao = None
        self.finalizado = True
        self._habilitar(True)
        self.desenhar()

        nome = self.algoritmo.get()
        ordem = self.resultado.ordem_exploracao
        linhas = [f"Algoritmo: {nome}",
                  f"Vértices explorados: {self.indice} de {len(ordem)}",
                  f"Tempo da busca (sem animação): "
                  f"{self.tempo_busca * 1000:.3f} ms"]
        if self._encontrou():
            caminho = self.resultado.caminho
            self.status.set("Caminho encontrado.")
            linhas += [f"Distância: {self.resultado.distancia:.3f}",
                       f"Arestas no caminho: {len(caminho) - 1}",
                       "Caminho: " + self._resumir(caminho)]
        elif self.indice < len(ordem):
            self.status.set("Busca interrompida antes de chegar ao destino.")
        elif nome == "Hill Climbing":
            self.status.set("Hill Climbing parou em um mínimo local; "
                            "destino não alcançado.")
        else:
            self.status.set("Não existe caminho entre origem e destino "
                            "(rede desconexa).")
        self.info.set("\n".join(linhas))


    @staticmethod
    def _resumir(caminho: list[int], limite: int = 16) -> str:
        """Abrevia caminhos longos para o painel não esconder a legenda."""
        if len(caminho) > limite:
            metade = limite // 2
            caminho = [*caminho[:metade], "…", *caminho[-metade:]]
        return " → ".join(map(str, caminho))


def executar() -> None:
    raiz = tk.Tk()
    Interface(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    executar()
