"""
Evolução multiobjetivo: custo e tempo de entrega ao mesmo tempo (Tema 38)
==========================================================================

Experimento do artigo: NSGA-II x Soma Ponderada (GA mono-objetivo) em um
problema SINTÉTICO de roteamento de veículos com dois objetivos:

  f1 = custo diário da operação (R$)  = custo fixo por veículo usado
                                        + custo por km rodado
  f2 = tempo médio de entrega (h)     = média, sobre os clientes, do
                                        instante em que cada um é atendido

Os dois objetivos são conflitantes: usar mais veículos (e rotas mais curtas)
reduz o tempo médio de entrega, mas aumenta o custo fixo e, em geral, a
quilometragem total (mais idas e voltas ao depósito).

Como rodar (Python 3.10+):
    pip install pymoo==0.6.2 numpy scipy matplotlib
    python experimento.py              # 30 repetições (~20 min em 2 núcleos)
    python experimento.py --reps 5     # teste rápido

Saída: ../resultados/execucoes.json (dados brutos). As figuras e as métricas
são geradas depois por analise.py.
"""

import argparse
import json
import os
import time
from multiprocessing import Pool

import numpy as np

from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.operators.sampling.rnd import PermutationRandomSampling
from pymoo.operators.crossover.ox import OrderCrossover
from pymoo.operators.mutation.inversion import InversionMutation
from pymoo.optimize import minimize
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting

# ---------------------------------------------------------------------------
# 1. PARÂMETROS DO CENÁRIO (ajuste aqui para explorar outros cenários)
# ---------------------------------------------------------------------------
SEED_INSTANCIA = 42      # semente que gera as coordenadas dos clientes
N_CLIENTES = 50          # número de clientes
K_MAX = 8                # tamanho máximo da frota disponível
LADO_KM = 100.0          # clientes espalhados num quadrado de 100 x 100 km
VELOCIDADE_KMH = 40.0    # velocidade média (urbano/regional)
SERVICO_H = 10 / 60      # 10 minutos de parada em cada cliente
CUSTO_FIXO = 250.0       # R$ por veículo usado no dia (motorista + diária)
CUSTO_KM = 2.50          # R$ por km (combustível + desgaste)

# Parâmetros dos algoritmos
POP = 100                # tamanho da população
GERACOES = 500           # gerações -> 50.000 avaliações por execução
PESOS = np.round(np.linspace(0, 1, 11), 2)  # pesos da soma ponderada
N_REPETICOES = 30

AQUI = os.path.dirname(os.path.abspath(__file__))
DIR_FIG = os.path.join(AQUI, "..", "figuras")
DIR_RES = os.path.join(AQUI, "..", "resultados")


def gerar_instancia(seed=SEED_INSTANCIA):
    rng = np.random.default_rng(seed)
    clientes = rng.uniform(0, LADO_KM, size=(N_CLIENTES, 2))
    deposito = np.array([[LADO_KM / 2, LADO_KM / 2]])
    pontos = np.vstack([deposito, clientes])          # índice 0 = depósito
    dif = pontos[:, None, :] - pontos[None, :, :]
    dist = np.sqrt((dif ** 2).sum(-1))
    return pontos, dist


PONTOS, DIST = gerar_instancia()


# ---------------------------------------------------------------------------
# 2. REPRESENTAÇÃO E DECODIFICAÇÃO
# Cromossomo = permutação de N + K_MAX - 1 genes. Genes < N são clientes;
# genes >= N são "separadores" que encerram uma rota e iniciam a próxima.
# Rotas vazias são descartadas, então o número de veículos é variável
# (de 1 a K_MAX) e emerge da própria evolução.
# ---------------------------------------------------------------------------
def decodificar(x):
    rotas, atual = [], []
    for g in x:
        if g >= N_CLIENTES:
            if atual:
                rotas.append(atual)
            atual = []
        else:
            atual.append(int(g) + 1)                 # nó no grafo (0 = depósito)
    if atual:
        rotas.append(atual)
    return rotas


def avaliar_rotas(rotas):
    """Retorna (custo R$, tempo médio de entrega h, km totais, nº veículos)."""
    km_total, soma_chegadas = 0.0, 0.0
    for rota in rotas:
        t, anterior = 0.0, 0
        for no in rota:
            d = DIST[anterior, no]
            km_total += d
            t += d / VELOCIDADE_KMH
            soma_chegadas += t          # instante em que o cliente é atendido
            t += SERVICO_H
            anterior = no
        km_total += DIST[anterior, 0]   # retorno ao depósito
    custo = CUSTO_FIXO * len(rotas) + CUSTO_KM * km_total
    return custo, soma_chegadas / N_CLIENTES, km_total, len(rotas)


def avaliar_populacao(X):
    """Versão vetorizada de avaliar_rotas para uma população inteira.
    Truque: cada separador é tratado como uma volta ao depósito (nó 0);
    separadores consecutivos geram trechos 0->0 de distância zero."""
    X = np.asarray(X)
    nos = np.where(X < N_CLIENTES, X + 1, 0)
    zeros = np.zeros((len(X), 1), dtype=nos.dtype)
    seq = np.hstack([zeros, nos, zeros])                  # 0 ... 0
    trecho = DIST[seq[:, :-1], seq[:, 1:]]                # km de cada trecho
    km = trecho.sum(1)
    eh_cliente = seq > 0
    # nº de veículos = nº de rotas não vazias (cliente precedido de depósito)
    veic = (eh_cliente[:, 1:] & ~eh_cliente[:, :-1]).sum(1)
    # tempo acumulado; zera a cada passagem pelo depósito
    a = trecho / VELOCIDADE_KMH + SERVICO_H * eh_cliente[:, :-1]
    C = np.hstack([zeros.astype(float), np.cumsum(a, 1)])
    idx = np.where(~eh_cliente, np.arange(seq.shape[1]), 0)
    ultimo_dep = np.maximum.accumulate(idx, axis=1)       # último depósito
    linhas = np.arange(len(X))[:, None]
    chegada = C[:, 1:] - C[linhas, ultimo_dep[:, :-1]]
    soma = (chegada * eh_cliente[:, 1:]).sum(1)
    custo = CUSTO_FIXO * veic + CUSTO_KM * km
    return custo, soma / N_CLIENTES, km, veic


class Roteamento2Obj(Problem):
    def __init__(self):
        super().__init__(n_var=N_CLIENTES + K_MAX - 1, n_obj=2, xl=0,
                         xu=N_CLIENTES + K_MAX - 2, vtype=int)

    def _evaluate(self, X, out, *args, **kwargs):
        c, t, _, _ = avaliar_populacao(X)
        out["F"] = np.column_stack([c, t])


class SomaPonderada(Problem):
    """f = w * custo_normalizado + (1 - w) * tempo_normalizado."""

    def __init__(self, w, ideal, nadir):
        super().__init__(n_var=N_CLIENTES + K_MAX - 1, n_obj=1, xl=0,
                         xu=N_CLIENTES + K_MAX - 2, vtype=int)
        self.w, self.ideal, self.escala = w, ideal, nadir - ideal

    def _evaluate(self, X, out, *args, **kwargs):
        c, t, _, _ = avaliar_populacao(X)
        fn = (np.column_stack([c, t]) - self.ideal) / self.escala
        out["F"] = (self.w * fn[:, 0] + (1 - self.w) * fn[:, 1])[:, None]


def operadores():
    return dict(sampling=PermutationRandomSampling(),
                crossover=OrderCrossover(prob=0.9),
                mutation=InversionMutation(prob=0.6),
                eliminate_duplicates=True)


def objetivos(x):
    c, t, _, _ = avaliar_rotas(decodificar(x))
    return np.array([c, t])


def nao_dominados(F, X=None):
    idx = NonDominatedSorting().do(F, only_non_dominated_front=True)
    F_nd = F[idx]
    # remove duplicatas de objetivos
    _, uniq = np.unique(np.round(F_nd, 6), axis=0, return_index=True)
    idx = idx[np.sort(uniq)]
    return (F[idx], X[idx]) if X is not None else F[idx]


# ---------------------------------------------------------------------------
# 3. UMA REPETIÇÃO = NSGA-II + duas variantes de Soma Ponderada
#   SP-total : 11 pesos dividindo o MESMO orçamento total do NSGA-II
#   SP-11x   : 11 pesos, cada um com o orçamento inteiro do NSGA-II
# ---------------------------------------------------------------------------
def uma_repeticao(seed):
    t0 = time.time()
    res = {}

    # --- NSGA-II -----------------------------------------------------------
    r = minimize(Roteamento2Obj(), NSGA2(pop_size=POP, **operadores()),
                 ("n_gen", GERACOES), seed=seed, save_history=True,
                 verbose=False)
    F_hist = [h.opt.get("F").copy() for h in r.history[::10]]
    F_nd, X_nd = nao_dominados(r.F, r.X)
    res["NSGA-II"] = dict(F=F_nd.tolist(), X=X_nd.tolist(),
                          hist=[f.tolist() for f in F_hist])

    # --- Soma ponderada -----------------------------------------------------
    for nome, n_gen in (("SP-total", GERACOES // len(PESOS)),
                        ("SP-11x", GERACOES)):
        sols = {}
        # extremos primeiro (w=1 só custo; w=0 só tempo) para normalizar
        ideal0, nadir0 = np.array([0.0, 0.0]), np.array([1.0, 1.0])
        for w in (1.0, 0.0):
            p = SomaPonderada(w, ideal0, nadir0)
            rr = minimize(p, GA(pop_size=POP, **operadores()),
                          ("n_gen", n_gen), seed=seed, verbose=False)
            sols[w] = rr.X
        f_custo, f_tempo = objetivos(sols[1.0]), objetivos(sols[0.0])
        ideal = np.array([f_custo[0], f_tempo[1]])
        nadir = np.array([f_tempo[0], f_custo[1]])
        for w in PESOS[1:-1]:
            p = SomaPonderada(w, ideal, nadir)
            rr = minimize(p, GA(pop_size=POP, **operadores()),
                          ("n_gen", n_gen), seed=seed, verbose=False)
            sols[float(w)] = rr.X
        Xs = np.array([sols[k] for k in sorted(sols)])
        Fs = np.array([objetivos(x) for x in Xs])
        F_nd, X_nd = nao_dominados(Fs, Xs)
        res[nome] = dict(F=F_nd.tolist(), X=X_nd.tolist(),
                         F_todos=Fs.tolist(), pesos=sorted(sols))
    res["seed"] = seed
    res["tempo_s"] = time.time() - t0
    print(f"  repetição seed={seed} ok em {res['tempo_s']:.1f}s", flush=True)
    return res


# ---------------------------------------------------------------------------
# 4. ANÁLISE
# ---------------------------------------------------------------------------
def escolha_gestor(F, X, orcamento, prazo):
    """Três regras simples de decisão sobre a frente de Pareto."""
    ordem = np.argsort(F[:, 0])
    F, X = F[ordem], X[ordem]
    escolhas = {}
    ok = F[:, 0] <= orcamento                       # (a) teto de orçamento
    i = np.where(ok)[0][np.argmin(F[ok, 1])]
    escolhas["Orçamento"] = i
    ok = F[:, 1] <= prazo                           # (b) prazo médio máximo
    i = np.where(ok)[0][np.argmin(F[ok, 0])]
    escolhas["Prazo"] = i
    # (c) ponto de joelho: maior distância à reta que liga os extremos
    Fn = (F - F.min(0)) / (F.max(0) - F.min(0))
    a, b = Fn[0], Fn[-1]
    v, w = b - a, Fn - a
    d = np.abs(v[0] * w[:, 1] - v[1] * w[:, 0]) / np.linalg.norm(v)
    escolhas["Joelho"] = int(np.argmax(d))
    return F, X, escolhas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=N_REPETICOES)
    ap.add_argument("--procs", type=int, default=os.cpu_count())
    args = ap.parse_args()
    os.makedirs(DIR_RES, exist_ok=True)
    os.makedirs(DIR_FIG, exist_ok=True)

    print(f"Rodando {args.reps} repetições em {args.procs} processos...")
    seeds = list(range(1, args.reps + 1))
    with Pool(args.procs) as pool:
        todos = pool.map(uma_repeticao, seeds)
    with open(os.path.join(DIR_RES, "execucoes.json"), "w", encoding="utf-8") as f:
        json.dump(todos, f)
    print("Execuções salvas em resultados/execucoes.json")


if __name__ == "__main__":
    main()
