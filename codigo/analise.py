"""
Análise dos resultados de experimento.py: métricas, testes estatísticos,
escolha do gestor e figuras (tons de cinza, conforme regra SBC/disciplina).

    python analise.py
"""
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu
from pymoo.indicators.hv import HV

import experimento as E

plt.rcParams.update({"font.family": "serif", "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False})
METODOS = ["NSGA-II", "SP-total", "SP-11x"]
ORCAMENTO = 3000.0   # R$/dia  -> regra (a) do gestor
PRAZO = 3.0          # horas   -> regra (b) do gestor

with open(os.path.join(E.DIR_RES, "execucoes.json"), encoding="utf-8") as f:
    RUNS = json.load(f)


from matplotlib.ticker import FuncFormatter
VIRG = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
MILHAR = FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", "."))


def salvar(fig, nome):
    for ax in fig.axes:
        if ax.get_xticks().size and ax.get_xlabel().startswith("Custo"):
            ax.xaxis.set_major_formatter(MILHAR)
        elif ax.get_xlabel():
            ax.xaxis.set_major_formatter(VIRG)
        if ax.get_ylabel():
            ax.yaxis.set_major_formatter(VIRG)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(E.DIR_FIG, f"{nome}.{ext}"), dpi=300,
                    bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- normalização
todos = np.vstack([np.array(r[m]["F"]) for r in RUNS for m in METODOS])
ref_front = E.nao_dominados(todos)
IDEAL, NADIR = ref_front.min(0), ref_front.max(0)
norm = lambda F: (np.asarray(F) - IDEAL) / (NADIR - IDEAL)
hv = HV(ref_point=np.array([1.1, 1.1]))


def suportados(Fn, n_pesos=2001):
    """Pontos que minimizam alguma soma ponderada (casco convexo)."""
    ws = np.linspace(0, 1, n_pesos)
    s = set(np.argmin(np.outer(ws, Fn[:, 0]) + np.outer(1 - ws, Fn[:, 1]),
                      axis=1))
    return len(s)


def maior_lacuna(Fn):
    Fn = Fn[np.argsort(Fn[:, 0])]
    return np.linalg.norm(np.diff(Fn, axis=0), axis=1).max() if len(Fn) > 1 else np.nan


def dominados_por(F, G):
    """Fração dos pontos de F dominados por algum ponto de G."""
    F, G = np.asarray(F), np.asarray(G)
    dom = ((G[None, :, :] <= F[:, None, :]).all(2)
           & (G[None, :, :] < F[:, None, :]).any(2)).any(1)
    return dom.mean()


def nao_suportados_uniao(r, n_pesos=2001):
    """Fração dos pontos do NSGA-II que continuam não dominados na união das
    frentes das três abordagens e NÃO minimizam nenhuma soma ponderada nela."""
    U = E.nao_dominados(np.vstack([np.array(r[m]["F"]) for m in METODOS]))
    Un = norm(U)
    ws = np.linspace(0, 1, n_pesos)
    sup = set(np.argmin(np.outer(ws, Un[:, 0]) + np.outer(1 - ws, Un[:, 1]), axis=1))
    F = np.round(np.array(r["NSGA-II"]["F"]), 6)
    Ur = np.round(U, 6)
    cont = 0
    for k, u in enumerate(Ur):
        if k not in sup and (F == u).all(1).any():
            cont += 1
    return cont / len(F)


met = {m: {"hv": [], "n": [], "cmin": [], "tmin": [], "lac": [], "sup": []}
       for m in METODOS}
extra = {"dom_sp11x": [], "nsup_uniao": []}
for r in RUNS:
    for m in METODOS:
        F = np.array(r[m]["F"])
        Fn = norm(F)
        met[m]["hv"].append(hv(Fn))
        met[m]["n"].append(len(F))
        met[m]["cmin"].append(F[:, 0].min())
        met[m]["tmin"].append(F[:, 1].min())
        met[m]["lac"].append(maior_lacuna(Fn))
        met[m]["sup"].append(suportados(Fn) / len(F))
    extra["dom_sp11x"].append(dominados_por(r["NSGA-II"]["F"], r["SP-11x"]["F"]))
    extra["nsup_uniao"].append(nao_suportados_uniao(r))

resumo = {}
print(f"Repetições: {len(RUNS)} | ideal={IDEAL.round(2)} nadir={NADIR.round(2)}")
print(f"{'Método':10s} {'HV':>16s} {'nº sol.':>12s} {'custo mín':>18s} "
      f"{'tempo mín':>14s} {'maior lacuna':>14s} {'%suportadas':>12s}")
for m in METODOS:
    d = {k: (float(np.mean(v)), float(np.std(v, ddof=1))) for k, v in met[m].items()}
    resumo[m] = d
    print(f"{m:10s} {d['hv'][0]:.4f}±{d['hv'][1]:.4f} {d['n'][0]:6.1f}±{d['n'][1]:4.1f} "
          f"{d['cmin'][0]:9.0f}±{d['cmin'][1]:6.0f} {d['tmin'][0]:6.2f}±{d['tmin'][1]:.2f} "
          f"{d['lac'][0]:6.3f}±{d['lac'][1]:.3f} {100*d['sup'][0]:6.1f}")

for k, v in extra.items():
    resumo["NSGA-II"][k] = (float(np.mean(v)), float(np.std(v, ddof=1)))
print(f"NSGA-II: dominadas pela SP-11x {100*np.mean(extra['dom_sp11x']):.1f}% | "
      f"não dominadas e não suportadas na união {100*np.mean(extra['nsup_uniao']):.1f}%")

testes = {}
for m in ("SP-total", "SP-11x"):
    for k in ("hv", "n", "lac"):
        u, p = mannwhitneyu(met["NSGA-II"][k], met[m][k], alternative="two-sided")
        testes[f"NSGA-II x {m} [{k}]"] = float(p)
        print(f"Mann-Whitney NSGA-II x {m} [{k}]: U={u:.0f}, p={p:.2e}")

tempos = [r["tempo_s"] for r in RUNS]

# ------------------------------------------------- execução mediana (NSGA-II)
hv_nsga = np.array(met["NSGA-II"]["hv"])
i_med = int(np.argsort(hv_nsga)[len(hv_nsga) // 2])
run = RUNS[i_med]
F_ns, X_ns = np.array(run["NSGA-II"]["F"]), np.array(run["NSGA-II"]["X"])
F_ns, X_ns, esc = E.escolha_gestor(F_ns, X_ns, ORCAMENTO, PRAZO)
F_sp = np.array(run["SP-11x"]["F"])
F_spt = np.array(run["SP-total"]["F"])

tabela_gestor = []
print(f"\nExecução mediana: seed={run['seed']}, HV={hv_nsga[i_med]:.4f}, "
      f"{len(F_ns)} soluções")
extremos = {"Menor custo": 0, "Menor tempo": len(F_ns) - 1}
for nome, i in list(extremos.items()) + list(esc.items()):
    c, t, km, v = E.avaliar_rotas(E.decodificar(X_ns[i]))
    tabela_gestor.append(dict(regra=nome, custo=c, tempo=t, km=km, veiculos=v))
    print(f"  {nome:12s} custo=R$ {c:8.2f} tempo={t:5.2f} h km={km:6.1f} veículos={v}")

# soma ponderada da mesma repetição
tabela_sp = []
for F in np.array(run["SP-11x"]["F_todos"]):
    tabela_sp.append(F.tolist())

with open(os.path.join(E.DIR_RES, "resumo.json"), "w", encoding="utf-8") as f:
    json.dump(dict(resumo=resumo, testes=testes, ideal=IDEAL.tolist(),
                   nadir=NADIR.tolist(), seed_mediana=run["seed"],
                   hv_mediana=float(hv_nsga[i_med]), gestor=tabela_gestor,
                   n_frente_mediana=len(F_ns), sp11x_mesma_seed=tabela_sp,
                   pesos=run["SP-11x"]["pesos"],
                   tempo_medio_rep_s=float(np.mean(tempos)),
                   orcamento=ORCAMENTO, prazo=PRAZO), f, indent=1,
              ensure_ascii=False)

# ----------------------------------------------------------- Figura: frentes
fig, ax = plt.subplots(figsize=(6.2, 3.9))
ax.plot(F_ns[:, 0], F_ns[:, 1], "o", ms=4, mfc="white", mec="black",
        label=f"NSGA-II ({len(F_ns)} soluções)")
o = np.argsort(F_sp[:, 0])
ax.plot(F_sp[o, 0], F_sp[o, 1], "s", ms=6, color="0.45",
        label=f"Soma ponderada SP-11x ({len(F_sp)})")
ax.plot(F_spt[:, 0], F_spt[:, 1], "^", ms=6, color="0.75", mec="0.3",
        label=f"Soma ponderada SP-total ({len(F_spt)})")
marc = {"Orçamento": "(a)", "Prazo": "(b)", "Joelho": "(c)"}
desl = {"Orçamento": (-22, -20), "Prazo": (10, 10), "Joelho": (6, 12)}
for nome, i in esc.items():
    ax.annotate(marc[nome], F_ns[i], xytext=desl[nome], textcoords="offset points",
                fontsize=9, arrowprops=dict(arrowstyle="-", lw=0.6))
ax.axvline(ORCAMENTO, ls=":", lw=0.8, color="0.4")
ax.axhline(PRAZO, ls=":", lw=0.8, color="0.4")
ax.set_xlabel("Custo diário da operação (R\\$)")
ax.set_ylabel("Tempo médio de entrega (h)")
ax.legend(frameon=False, fontsize=8)
salvar(fig, "fig_frentes")

# ------------------------------------------------------------ Figura: boxplot
fig, axs = plt.subplots(1, 2, figsize=(6.2, 2.7))
dados = [met[m]["hv"] for m in METODOS]
axs[0].boxplot(dados, tick_labels=METODOS, patch_artist=True,
               boxprops=dict(facecolor="0.85"), medianprops=dict(color="black"))
axs[0].set_ylabel("Hipervolume (normalizado)")
dados = [met[m]["n"] for m in METODOS]
axs[1].boxplot(dados, tick_labels=METODOS, patch_artist=True,
               boxprops=dict(facecolor="0.85"), medianprops=dict(color="black"))
axs[1].set_ylabel("Nº de soluções não dominadas")
for a in axs:
    a.tick_params(axis="x", labelsize=8)
fig.tight_layout()
salvar(fig, "fig_boxplot")

# -------------------------------------------------------- Figura: convergência
curvas = np.array([[hv(norm(F)) for F in r["NSGA-II"]["hist"]] for r in RUNS])
ger = np.arange(curvas.shape[1]) * 10 + 1
avals = ger * E.POP / 1000
mu, sd = curvas.mean(0), curvas.std(0, ddof=1)
fig, ax = plt.subplots(figsize=(6.2, 2.3))
ax.plot(avals, mu, color="black", lw=1.2, label="NSGA-II (média)")
ax.fill_between(avals, np.clip(mu - sd, 0, None), mu + sd, color="0.8",
                label="± 1 desvio padrão")
for m, ls in (("SP-total", "--"), ("SP-11x", ":")):
    ax.axhline(resumo[m]["hv"][0], ls=ls, color="0.35", lw=1,
               label=f"{m} (média final)")
ax.set_xlabel("Avaliações da função objetivo (milhares)")
ax.set_ylabel("Hipervolume")
ax.legend(frameon=False, fontsize=8, loc="center right",
          bbox_to_anchor=(1.0, 0.52))
salvar(fig, "fig_convergencia")

# ------------------------------------------------------------- Figura: rotas
estilos = ["-", "--", "-.", ":", (0, (5, 1)), (0, (3, 1, 1, 1)), (0, (1, 1)),
           (0, (8, 2))]
fig, axs = plt.subplots(1, 3, figsize=(6.6, 2.5))
for ax, (titulo, i) in zip(axs, [("Menor custo", 0), ("Joelho (c)", esc["Joelho"]),
                                ("Menor tempo", len(F_ns) - 1)]):
    rotas = E.decodificar(X_ns[i])
    c, t, km, v = E.avaliar_rotas(rotas)
    for k, rota in enumerate(rotas):
        p = E.PONTOS[[0] + rota + [0]]
        ax.plot(p[:, 0], p[:, 1], ls=estilos[k % len(estilos)], lw=0.8,
                color=str(0.0 + 0.5 * (k % 2)))
    ax.plot(E.PONTOS[1:, 0], E.PONTOS[1:, 1], "o", ms=2.2, color="black")
    ax.plot(*E.PONTOS[0], "s", ms=6, color="white", mec="black", mew=1.2)
    ax.set_title(f"{titulo}\n{v} veíc. | R\\$ {c:,.0f}".replace(",", ".") + f" | {t:.2f} h".replace(".", ","),
                 fontsize=8)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_aspect("equal")
    for s in ax.spines.values():
        s.set_visible(True); s.set_linewidth(0.5)
fig.tight_layout()
salvar(fig, "fig_rotas")
print("\nFiguras salvas em figuras/")
