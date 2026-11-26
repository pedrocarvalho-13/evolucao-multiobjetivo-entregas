"""
Verificação das tabelas do artigo a partir da execução do programa.

Recalcula, DIRETAMENTE dos dados brutos (resultados/execucoes.json gerado por
experimento.py), todos os valores das Tabelas 2 e 3 do artigo, imprime as
tabelas no terminal e confere se cada valor aparece igual no artigo.tex.

    python experimento.py        # gera os dados brutos (30 repetições)
    python verificar_tabelas.py  # reconstrói e confere as tabelas

Sai com código 0 se tudo confere e 1 se algum valor divergir.
"""
import json
import os
import re
import sys

import numpy as np
from pymoo.indicators.hv import HV

import experimento as E

METODOS = ["NSGA-II", "SP-total", "SP-11x"]
ORCAMENTO, PRAZO = 3000.0, 3.0   # mesmas regras do gestor do artigo
TEX = os.path.join(E.AQUI, "..", "artigo.tex")


def br(x, casas):
    s = f"{x:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def main():
    with open(os.path.join(E.DIR_RES, "execucoes.json"), encoding="utf-8") as f:
        runs = json.load(f)
    print(f"Dados brutos: {len(runs)} repetições (sementes "
          f"{min(r['seed'] for r in runs)} a {max(r['seed'] for r in runs)})\n")

    # ------------------------------------------------ Tabela 2 (métricas)
    todos = np.vstack([np.array(r[m]["F"]) for r in runs for m in METODOS])
    ref = E.nao_dominados(todos)
    ideal, nadir = ref.min(0), ref.max(0)
    hv = HV(ref_point=np.array([1.1, 1.1]))
    met = {m: {k: [] for k in ("hv", "n", "cmin", "tmin", "lac")} for m in METODOS}
    for r in runs:
        for m in METODOS:
            F = np.array(r[m]["F"])
            Fn = (F - ideal) / (nadir - ideal)
            met[m]["hv"].append(hv(Fn))
            met[m]["n"].append(len(F))
            met[m]["cmin"].append(F[:, 0].min())
            met[m]["tmin"].append(F[:, 1].min())
            o = Fn[np.argsort(Fn[:, 0])]
            met[m]["lac"].append(np.linalg.norm(np.diff(o, axis=0), axis=1).max())

    linhas2 = [("Hipervolume", "hv", 3), ("Nº de soluções não dominadas", "n", 1),
               ("Custo mínimo (R$)", "cmin", 0), ("Tempo médio mínimo (h)", "tmin", 2),
               ("Maior lacuna (normalizada)", "lac", 3)]
    esperado = []
    print("TABELA 2 - Métricas nas 30 repetições (média ± desvio padrão)")
    print(f"{'Métrica':30s}" + "".join(f"{m:>20s}" for m in METODOS))
    for nome, k, c in linhas2:
        cel = []
        for m in METODOS:
            v = np.array(met[m][k])
            cel.append(f"{br(v.mean(), c)} ± {br(v.std(ddof=1), c)}")
            esperado.append((f"Tabela 2 / {nome} / {m}",
                             f"{br(v.mean(), c)} $\\pm$ {br(v.std(ddof=1), c)}"))
        print(f"{nome:30s}" + "".join(f"{x:>20s}" for x in cel))

    # ------------------------------------------------ Tabela 3 (gestor)
    hvs = np.array(met["NSGA-II"]["hv"])
    i_med = int(np.argsort(hvs)[len(hvs) // 2])
    run = runs[i_med]
    F, X, esc = E.escolha_gestor(np.array(run["NSGA-II"]["F"]),
                                 np.array(run["NSGA-II"]["X"]), ORCAMENTO, PRAZO)
    regras = [("Extremo: menor custo", 0), ("(a) Orçamento", esc["Orçamento"]),
              ("(b) Prazo", esc["Prazo"]), ("(c) Ponto de joelho", esc["Joelho"]),
              ("Extremo: menor tempo", len(F) - 1)]
    print(f"\nTABELA 3 - Escolhas do gestor na execução de HV mediano "
          f"(semente {run['seed']}, {len(F)} soluções)")
    print(f"{'Regra':24s}{'Custo (R$/dia)':>16s}{'Tempo (h)':>11s}{'km':>8s}{'Veíc.':>7s}")
    for nome, i in regras:
        c, t, km, v = E.avaliar_rotas(E.decodificar(X[i]))
        print(f"{nome:24s}{br(c, 0):>16s}{br(t, 2):>11s}{br(km, 0):>8s}{v:>7d}")
        esperado.append((f"Tabela 3 / {nome}",
                         f"{br(c, 0)} & {br(t, 2)} & {br(km, 0)} & {v}"))

    # ------------------------------------------------ conferência com o artigo
    if not os.path.exists(TEX):
        print("\n(artigo.tex não encontrado: conferência com o texto pulada)")
        return 0
    tex = re.sub(r"\s+", " ", open(TEX, encoding="utf-8").read())
    erros = [(onde, val) for onde, val in esperado if val not in tex]
    print(f"\nConferência com artigo.tex: {len(esperado) - len(erros)}/{len(esperado)} "
          "valores idênticos.")
    for onde, val in erros:
        print(f"  DIVERGE: {onde}: esperado '{val}'")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
