"""
CONTEÚDO DO ARTIGO (fonte única para o .tex e o .docx).

Marcações usadas no texto:
  *itálico*        $matemática LaTeX$       {real} -> "R$ "
  [@chave]         citação entre colchetes: [Deb et al. 2002]
  [@a; @b]         várias citações
  @chave           citação no texto: Deb et al. [2002]
  {ref:rotulo}     número de seção/figura/tabela/equação
  <<VALOR>>        número vindo de resultados/resumo.json (ver valores_de)
"""

CABECALHO = dict(
    titulo="Evolução Multiobjetivo no Roteamento de Entregas: "
           "Custo e Tempo de Entrega ao Mesmo Tempo com NSGA-II",
    title="Multi-Objective Evolution for Delivery Routing: "
          "Cost and Delivery Time at Once with NSGA-II",
    autores_tex=(r"Enzo Figueiredo Feitosa$^{1}$, Mateus Henrique de Araújo Santos$^{1}$, "
                 r"Pedro Carvalho$^{1}$,\\ Luiz Henrique$^{1}$, "
                 r"Anthony Yuri Feitosa França$^{1}$, Guilherme Santos$^{1}$"),
    autores_docx=("Enzo Figueiredo Feitosa¹, Mateus Henrique de Araújo Santos¹, "
                  "Pedro Carvalho¹, Luiz Henrique¹, Anthony Yuri Feitosa França¹, "
                  "Guilherme Santos¹"),
    orientacao="Professor: Sérgio Santana -- Disciplina: Machine Learning e Data Science",
    afiliacao=r"$^{1}$Curso de Sistemas de Informação -- Universidade Tiradentes (UNIT) -- Aracaju/SE",
    afiliacao_docx="¹Curso de Sistemas de Informação – Universidade Tiradentes (UNIT) – Aracaju/SE",
    emails="enzo.figueiredo@souunit.com.br, mateus.henrique05@souunit.com.br, pedro.gcarvalho@souunit.com.br, luiz.hsilva@souunit.com.br, anthony.yuri@souunit.com.br, guilherme.santos1102@souunit.com.br",
    emails_tex=r"""enzo.figueiredo@souunit.com.br, mateus.henrique05@souunit.com.br,\\
    pedro.gcarvalho@souunit.com.br, luiz.hsilva@souunit.com.br,\\
    anthony.yuri@souunit.com.br, guilherme.santos1102@souunit.com.br""",
)

REPOSITORIO = "https://github.com/pedrocarvalho-13/evolucao-multiobjetivo-entregas"

PALAVRAS = ("otimização multiobjetivo, NSGA-II, frente de Pareto, "
            "roteamento de veículos, soma ponderada.")
KEYWORDS = ("multi-objective optimization, NSGA-II, Pareto front, "
            "vehicle routing, weighted sum.")

RESUMO = (
    "Empresas de entrega querem baixo custo e prazo curto, objetivos que se opõem, e "
    "otimizar uma soma ponderada dos dois devolve uma só resposta, que esconde as "
    "alternativas. Este trabalho aplica o NSGA-II a um problema sintético de roteamento "
    "com 50 clientes e até 8 veículos, minimizando o custo diário e o tempo médio de "
    "entrega, e o compara com a soma ponderada em 30 repetições. Com o mesmo orçamento de "
    "avaliações, o NSGA-II obteve hipervolume de <<HV_NS>>, contra <<HV_SPT>>. Com onze "
    "vezes mais avaliações, a soma ponderada chegou a <<HV_SP11>>, mas ofereceu <<N_SP11>> "
    "alternativas por execução, contra <<N_NS>> do NSGA-II. A frente obtida permite ao "
    "gestor escolher a solução por orçamento, por prazo ou pelo ponto de joelho."
)

ABSTRACT = (
    "Delivery companies want low cost and short lead times, two conflicting goals, and "
    "optimizing a weighted sum of both returns a single answer that hides the "
    "alternatives. This work applies NSGA-II to a synthetic routing problem with 50 "
    "customers and up to 8 vehicles, minimizing daily cost and mean delivery time, and "
    "compares it with the weighted-sum method over 30 runs. Under the same evaluation "
    "budget, NSGA-II reached a hypervolume of <<HV_NS_EN>>, versus <<HV_SPT_EN>>. With "
    "eleven times more evaluations, the weighted sum reached <<HV_SP11_EN>>, but offered "
    "<<N_SP11_EN>> alternatives per run, against <<N_NS_EN>> for NSGA-II. The resulting "
    "front lets the manager pick a solution by budget, by deadline or by the knee point."
)


def valores_de(R, br):
    r = R["resumo"]
    m = lambda k, c, casas: br(r[k][c][0], casas)
    s = lambda k, c, casas: br(r[k][c][1], casas)
    en = lambda x, casas: f"{x:,.{casas}f}"
    v = {}
    for tag, k in (("NS", "NSGA-II"), ("SPT", "SP-total"), ("SP11", "SP-11x")):
        v[f"HV_{tag}"] = m(k, "hv", 3); v[f"HV_{tag}_SD"] = s(k, "hv", 3)
        v[f"HV_{tag}_EN"] = en(r[k]["hv"][0], 3)
        v[f"N_{tag}"] = m(k, "n", 1); v[f"N_{tag}_SD"] = s(k, "n", 1)
        v[f"N_{tag}_EN"] = en(r[k]["n"][0], 1)
        v[f"CMIN_{tag}"] = m(k, "cmin", 0); v[f"CMIN_{tag}_SD"] = s(k, "cmin", 0)
        v[f"TMIN_{tag}"] = m(k, "tmin", 2); v[f"TMIN_{tag}_SD"] = s(k, "tmin", 2)
        v[f"LAC_{tag}"] = m(k, "lac", 3); v[f"LAC_{tag}_SD"] = s(k, "lac", 3)
        v[f"SUP_{tag}"] = br(100 * r[k]["sup"][0], 0)
    for k, p in R["testes"].items():
        alvo = "SPT" if "SP-total" in k else "SP11"
        met = k.split("[")[1][:-1].upper()
        if p < 1e-3:
            mant, exp = f"{p:.1e}".split("e")
            txt = mant.replace(".", "{,}") + "\\times 10^{" + str(int(exp)) + "}"
        else:
            txt = br(p, 3).replace(",", "{,}")
        v[f"P_{alvo}_{met}"] = txt
    v["TEMPO_REP"] = br(R["tempo_medio_rep_s"], 0)
    v["SEED_MED"] = R["seed_mediana"]
    v["HV_MED"] = br(R["hv_mediana"], 3)
    v["N_MED"] = R["n_frente_mediana"]
    v["ORC"] = br(R["orcamento"], 0)
    v["PRAZO"] = br(R["prazo"], 1)
    g = {x["regra"]: x for x in R["gestor"]}
    for nome, tag in (("Menor custo", "MC"), ("Menor tempo", "MT"), ("Orçamento", "OR"),
                      ("Prazo", "PZ"), ("Joelho", "JO")):
        v[f"{tag}_C"] = br(g[nome]["custo"], 0)
        v[f"{tag}_T"] = br(g[nome]["tempo"], 2)
        v[f"{tag}_KM"] = br(g[nome]["km"], 0)
        v[f"{tag}_V"] = g[nome]["veiculos"]
    # comparações derivadas usadas no texto
    mc, mt, jo = g["Menor custo"], g["Menor tempo"], g["Joelho"]
    v["JO_DT_PCT"] = br(100 * (mc["tempo"] - jo["tempo"]) / mc["tempo"], 0)
    v["JO_DC_PCT"] = br(100 * (jo["custo"] - mc["custo"]) / mc["custo"], 0)
    v["MT_DC_PCT"] = br(100 * (mt["custo"] - jo["custo"]) / jo["custo"], 0)
    v["MT_DT_PCT"] = br(100 * (jo["tempo"] - mt["tempo"]) / jo["tempo"], 0)
    v["IDEAL_C"] = br(R["ideal"][0], 0); v["NADIR_C"] = br(R["nadir"][0], 0)
    v["IDEAL_T"] = br(R["ideal"][1], 2); v["NADIR_T"] = br(R["nadir"][1], 2)
    v["RAZ_N"] = br(r["NSGA-II"]["n"][0] / r["SP-11x"]["n"][0], 1)
    v["DOM_NS"] = br(100 * r["NSGA-II"]["dom_sp11x"][0], 0)
    v["NSUP_U"] = br(100 * r["NSGA-II"]["nsup_uniao"][0], 0)
    sp = min(R["sp11x_mesma_seed"], key=lambda f: f[0])
    v["SP11_MC_C"] = br(sp[0], 0); v["SP11_MC_T"] = br(sp[1], 2)
    return v


BLOCOS = [
# ============================================================ 1. INTRODUÇÃO
("sec", "Introdução", "sec:intro"),
("p", "No Brasil, o custo logístico deve chegar a 15,5% do PIB em 2025, dos quais 8,5 "
      "pontos percentuais correspondem ao transporte, segundo levantamento do ILOS "
      "divulgado por [@mundolog2025]. Para uma transportadora ou um e-commerce, cada "
      "quilômetro rodado e cada veículo na rua pesam no resultado, ao mesmo tempo em que o "
      "cliente espera entregas cada vez mais rápidas. O gestor enfrenta, portanto, dois "
      "objetivos que se opõem: reduzir o custo da operação e reduzir o tempo até a entrega."),
("p", "O conflito é estrutural: a forma mais barata de atender um conjunto de clientes "
      "costuma ser concentrar as entregas em poucos veículos com rotas longas, e a mais "
      "rápida é dividi-los entre muitos veículos, o que aumenta o custo fixo da frota e a "
      "quilometragem. Não há, em geral, uma solução melhor nos dois critérios, e sim um "
      "conjunto de soluções de compromisso, a *frente de Pareto*, em que melhorar um "
      "objetivo exige piorar o outro [@miettinen1999; @deb2001]."),
("p", "Na prática, é comum atribuir pesos ao custo e ao tempo e otimizar a soma "
      "ponderada [@marler2004]. Essa estratégia exige escolher os pesos *antes* de "
      "conhecer as alternativas, devolve uma única resposta por combinação de pesos e, "
      "como mostraram @das1997, não alcança soluções em trechos não convexos da frente. "
      "Algoritmos evolutivos multiobjetivo, como o NSGA-II [@deb2002], evoluem uma "
      "população inteira e devolvem, em uma única execução, uma aproximação da frente."),
("p", "O objetivo deste trabalho é avaliar o NSGA-II como apoio à decisão entre custo e "
      "tempo de entrega em um problema de roteamento de veículos. Especificamente, "
      "busca-se: (i) modelar um problema sintético de roteamento com dois objetivos; "
      "(ii) obter a frente de Pareto com o NSGA-II; (iii) compará-la com a soma "
      "ponderada, sob o mesmo orçamento computacional e sob um orçamento onze vezes "
      "maior; e (iv) ilustrar a escolha de uma solução por critérios de negócio. A Seção "
      "{ref:sec:fund} apresenta a fundamentação; a Seção {ref:sec:metodo}, a metodologia; "
      "a Seção {ref:sec:impl}, a implementação; a Seção {ref:sec:res}, os resultados; e a "
      "Seção {ref:sec:conc}, as conclusões."),

# ============================================================ 2. FUNDAMENTAÇÃO
("sec", "Fundamentação Teórica", "sec:fund"),
("sub", "Otimização multiobjetivo e dominância de Pareto", "sec:pareto"),
("p", "Um problema multiobjetivo com $M$ objetivos a minimizar busca soluções "
      "$\\mathbf{x}$ que minimizem o vetor $\\mathbf{F}(\\mathbf{x}) = (f_1(\\mathbf{x}), "
      "\\ldots, f_M(\\mathbf{x}))$. As soluções são comparadas pela relação de "
      "*dominância* [@miettinen1999; @deb2001]: $\\mathbf{x}$ domina $\\mathbf{y}$ "
      "($\\mathbf{x} \\prec \\mathbf{y}$) quando não é pior em nenhum objetivo e é "
      "estritamente melhor em pelo menos um:"),
("eq", r"\mathbf{x} \prec \mathbf{y} \iff f_i(\mathbf{x}) \le f_i(\mathbf{y})\;\; \forall i \in \{1,\ldots,M\} \;\;\text{e}\;\; \exists j : f_j(\mathbf{x}) < f_j(\mathbf{y}).",
       "x ≺ y  ⇔  fᵢ(x) ≤ fᵢ(y) ∀ i ∈ {1, …, M}  e  ∃ j : fⱼ(x) < fⱼ(y)", "eq:dom"),
("p", "Uma solução que nenhuma outra domina é *Pareto-ótima*; a imagem dessas soluções "
      "no espaço dos objetivos é a *frente de Pareto*. Com dois objetivos, a frente é uma "
      "curva no plano custo $\\times$ tempo, de leitura simples para o tomador de decisão."),
("sub", "Algoritmos genéticos e o NSGA-II", "sec:nsga"),
("p", "Algoritmos genéticos melhoram uma população de soluções ao longo de gerações por "
      "seleção, cruzamento e mutação [@holland1975; @goldberg1989] e, por trabalharem com "
      "populações, adequam-se a problemas em que se deseja um conjunto de soluções "
      "[@coello2007]. O NSGA-II [@deb2002] junta pais e filhos a cada geração e os ordena "
      "em frentes sucessivas por *ordenação não dominada*: a primeira frente reúne as "
      "soluções que ninguém domina, a segunda, as dominadas apenas pela primeira, e assim "
      "por diante. A nova população é preenchida frente a frente, o que garante elitismo, "
      "e o desempate usa a *distância de aglomeração*, que favorece soluções em regiões "
      "menos povoadas e preserva a diversidade. A ordenação custa $O(MN^2)$ por geração, "
      "sendo $N$ o tamanho da população."),
("sub", "Soma ponderada e hipervolume", "sec:sp"),
("p", "A soma ponderada minimiza $\\sum_i w_i \\bar{f}_i(\\mathbf{x})$, com objetivos "
      "normalizados $\\bar{f}_i$ e pesos $w_i \\ge 0$ que somam um [@marler2004]. É simples, "
      "mas exige uma execução por vetor de pesos, alcança apenas as soluções da parte "
      "convexa da frente (soluções *suportadas*) e, com pesos uniformemente espaçados, "
      "tende a concentrar as soluções em poucas regiões [@das1997]."),
("p", "Para comparar frentes, é preciso medir ao mesmo tempo convergência e diversidade. "
      "O *hipervolume* [@zitzler1999] mede a área do espaço dos objetivos dominada pelo "
      "conjunto de soluções e limitada por um ponto de referência; quanto maior, melhor. "
      "É um dos poucos indicadores unários compatíveis com a dominância: se um conjunto "
      "domina outro, seu hipervolume é maior [@zitzler2003]."),
("sub", "Trabalhos relacionados", "sec:rel"),
("p", "O roteamento de veículos foi formulado por @dantzig1959 e é NP-difícil, o que "
      "motiva o uso de metaheurísticas [@toth2014]. @potvin2009 revisa algoritmos "
      "evolutivos para o problema, com destaque para representações por permutação. Na "
      "versão multiobjetivo, @jozefowiez2008 classificam os trabalhos pelos objetivos "
      "considerados (distância, número de veículos, equilíbrio de carga, janelas de tempo) "
      "e apontam os algoritmos evolutivos como a abordagem mais frequente. @garcia2010 "
      "incluem o tempo de entrega como objetivo, ao lado do número de rotas e da distância, "
      "e relatam resultados superiores aos do NSGA-II com um algoritmo próprio, que depois "
      "aprimoram com uma medida de similaridade entre soluções [@garcia2011]. Enquanto "
      "esses estudos buscam superar o estado da arte em instâncias de referência, o foco "
      "aqui é o apoio à decisão: mostrar, em uma instância controlada, o que o gestor ganha "
      "ao receber uma frente em vez de uma única solução."),

# ============================================================ 3. METODOLOGIA
("sec", "Metodologia", "sec:metodo"),
("sub", "Base de dados sintética", "sec:base"),
("p", "Conforme a delimitação do tema, foi usado um problema sintético, o que permite "
      "controlar o cenário e reproduzir os resultados. Foram gerados 50 clientes com "
      "coordenadas uniformes em um quadrado de 100 km $\\times$ 100 km (semente 42) e um "
      "depósito no centro; as distâncias são euclidianas. A frota é homogênea, com até "
      "$K_{\\max} = 8$ veículos que saem do depósito e retornam ao fim da rota, sem "
      "restrição de capacidade, como na entrega de encomendas pequenas. Os demais "
      "parâmetros, de ordem de grandeza plausível, estão na Tabela {ref:tab:param}. Não "
      "houve pré-processamento, pois os dados já são gerados no formato do modelo."),
("tab", "tab:param", "Parâmetros do cenário e dos algoritmos.", "ll",
 ["Parâmetro", "Valor"],
 [["Clientes / frota máxima", "50 / 8 veículos"],
  ["Velocidade média / parada por cliente", "40 km/h / 10 min"],
  ["Custo fixo por veículo / custo por km", "{real}250,00 por dia / {real}2,50"],
  ["População / gerações", "100 / 500 (50.000 avaliações)"],
  ["Cruzamento / mutação", "OX, taxa 0,9 / inversão, taxa 0,6"],
  ["Pesos da soma ponderada", "$w \\in \\{0; 0{,}1; \\ldots; 1\\}$ (11 pesos)"],
  ["Repetições independentes", "30 (sementes 1 a 30)"]]),
("sub", "Modelo e objetivos", "sec:modelo"),
("p", "Uma solução é um conjunto de rotas $r_1, \\ldots, r_K$, com $1 \\le K \\le K_{\\max}$, "
      "em que cada cliente aparece uma única vez. Sendo $c_F$ o custo fixo por veículo, "
      "$c_D$ o custo por km e $D$ a distância total (com retorno ao depósito), o primeiro "
      "objetivo é o custo diário $f_1$. O segundo, $f_2$, é o tempo médio de entrega: a "
      "média, sobre os $n = 50$ clientes, do instante $t_j$ em que o veículo chega ao "
      "cliente $j$, contado da saída do depósito e incluindo as paradas anteriores:"),
("eq", r"f_1 = c_F \cdot K + c_D \cdot D, \qquad f_2 = \frac{1}{n}\sum_{j=1}^{n} t_j.",
       "f₁ = c_F · K + c_D · D,     f₂ = (1/n) · ∑ⱼ tⱼ", "eq:obj"),
("p", "Um único veículo minimiza o custo fixo, mas o último cliente só é atendido no fim "
      "de uma rota longa; usar todos os veículos reduz o tempo médio, mas multiplica o "
      "custo fixo e as idas e voltas ao depósito."),
("sub", "Representação, operadores e abordagens comparadas", "sec:repr"),
("p", "Cada solução é uma permutação de $n + K_{\\max} - 1 = 57$ genes: os valores 0 a 49 "
      "são clientes e os valores 50 a 56 são *separadores* que encerram uma rota e iniciam "
      "a próxima. Rotas vazias são descartadas, de modo que o número de veículos emerge da "
      "evolução. Toda permutação é válida, o que permite usar o cruzamento por ordem (OX) "
      "[@davis1985], que preserva a ordem relativa dos genes dos pais, e a mutação por "
      "inversão, que inverte um trecho do cromossomo e pode reordenar uma rota ou mover "
      "clientes entre rotas. Indivíduos duplicados são eliminados."),
("p", "Três abordagens foram comparadas, com os mesmos operadores, população de 100 e a "
      "mesma semente em cada repetição. O *NSGA-II* executa 500 gerações (50.000 "
      "avaliações). A *SP-total* executa um algoritmo genético mono-objetivo para cada um "
      "dos 11 pesos, com 45 gerações cada, totalizando o mesmo orçamento. A *SP-11x* usa "
      "500 gerações por peso (550.000 avaliações) e verifica se as conclusões se mantêm "
      "sem limite de orçamento para a soma ponderada. Nas duas, minimiza-se "
      "$w \\bar{f}_1 + (1-w)\\bar{f}_2$, com $\\bar{f}_i = (f_i - f_i^{\\min})/(f_i^{\\max} "
      "- f_i^{\\min})$ e limites estimados pelas execuções extremas ($w = 1$ e $w = 0$) "
      "[@marler2004]; das 11 soluções, mantêm-se as não dominadas."),
("sub", "Métricas e protocolo de avaliação", "sec:metricas"),
("p", "Cada abordagem foi executada 30 vezes, com média e desvio padrão reportados. As "
      "métricas são: (i) o hipervolume, com objetivos normalizados pela frente de "
      "referência (união não dominada de todas as soluções encontradas) e ponto de "
      "referência $(1{,}1; 1{,}1)$; (ii) o número de soluções não dominadas oferecidas ao "
      "gestor; (iii) os melhores custo e tempo alcançados; e (iv) a maior lacuna, isto é, "
      "a maior distância normalizada entre soluções vizinhas da frente. As diferenças foram "
      "avaliadas pelo teste de Mann-Whitney [@mann1947], bilateral, com significância de 5%."),
("p", "Para ilustrar a decisão, tomou-se a execução do NSGA-II de hipervolume mediano e "
      "aplicaram-se três regras: (a) *orçamento*, a solução mais rápida com custo de até "
      "{real}<<ORC>>,00 por dia; (b) *prazo*, a mais barata com tempo médio de até "
      "<<PRAZO>> h; e (c) *ponto de joelho*, a de maior distância à reta que liga os "
      "extremos da frente normalizada, região em que pequenas melhoras em um objetivo "
      "passam a custar grandes pioras no outro e que costuma ser preferida pelos "
      "decisores [@branke2004]."),

# ============================================================ 4. IMPLEMENTAÇÃO
("sec", "Implementação e Experimentos", "sec:impl"),
("p", "O experimento foi implementado em Python 3.13 com a biblioteca pymoo 0.6.2 "
      "[@blank2020], que fornece o NSGA-II, o algoritmo genético mono-objetivo, os "
      "operadores de permutação e o hipervolume; NumPy 2.5 foi usado na avaliação "
      "vetorizada da população, SciPy 1.18 no teste estatístico e Matplotlib 3.11 nas "
      "figuras. Na avaliação, cada separador é tratado como uma passagem pelo depósito, em "
      "que o tempo acumulado é zerado, o que dispensa laços sobre as rotas. A execução "
      "ocorreu em ambiente Linux, com processador Intel Xeon de 2,1 GHz e dois processos "
      "paralelos, no ambiente da ferramenta de IA indicada na declaração ao final do "
      "artigo; cada repetição completa levou em média <<TEMPO_REP>> s, a maior parte "
      "gasta pela SP-11x. A análise, as figuras e a conferência das tabelas foram refeitas "
      "em um computador pessoal com Windows 11 e as mesmas versões das bibliotecas, com "
      "valores idênticos. Todos os valores das Tabelas {ref:tab:metricas} e "
      "{ref:tab:gestor} e das figuras foram produzidos pela execução do programa: "
      "o script *experimento.py* gera os dados brutos das 30 repetições, *analise.py* "
      "calcula as métricas e as figuras, e *verificar_tabelas.py* reconstrói as tabelas a "
      "partir desses dados e confere cada um de seus valores com o texto do artigo. Uma segunda "
      "execução completa, feita do zero, reproduziu os mesmos valores. Código, semente "
      "e resultados brutos estão disponíveis no repositório do sistema: "
      "<https://github.com/pedrocarvalho-13/evolucao-multiobjetivo-entregas>."),

# ============================================================ 5. RESULTADOS
("sec", "Resultados e Discussão", "sec:res"),
("sub", "Comparação quantitativa", "sec:quant"),
("p", "A Tabela {ref:tab:metricas} resume as métricas nas 30 repetições, e a Figura "
      "{ref:fig:box} mostra a dispersão do hipervolume e do número de soluções."),
("tab", "tab:metricas", "Métricas nas 30 repetições (média $\\pm$ desvio padrão). Custo "
        "e tempo mínimos referem-se à melhor solução de cada frente em cada objetivo.",
 "lccc",
 ["Métrica", "NSGA-II", "SP-total", "SP-11x"],
 [["Avaliações por repetição", "50.000", "$\\approx$ 49.500", "550.000"],
  ["Hipervolume", "<<HV_NS>> $\\pm$ <<HV_NS_SD>>", "<<HV_SPT>> $\\pm$ <<HV_SPT_SD>>",
   "<<HV_SP11>> $\\pm$ <<HV_SP11_SD>>"],
  ["Nº de soluções não dominadas", "<<N_NS>> $\\pm$ <<N_NS_SD>>",
   "<<N_SPT>> $\\pm$ <<N_SPT_SD>>", "<<N_SP11>> $\\pm$ <<N_SP11_SD>>"],
  ["Custo mínimo ({real})", "<<CMIN_NS>> $\\pm$ <<CMIN_NS_SD>>",
   "<<CMIN_SPT>> $\\pm$ <<CMIN_SPT_SD>>", "<<CMIN_SP11>> $\\pm$ <<CMIN_SP11_SD>>"],
  ["Tempo médio mínimo (h)", "<<TMIN_NS>> $\\pm$ <<TMIN_NS_SD>>",
   "<<TMIN_SPT>> $\\pm$ <<TMIN_SPT_SD>>", "<<TMIN_SP11>> $\\pm$ <<TMIN_SP11_SD>>"],
  ["Maior lacuna (normalizada)", "<<LAC_NS>> $\\pm$ <<LAC_NS_SD>>",
   "<<LAC_SPT>> $\\pm$ <<LAC_SPT_SD>>", "<<LAC_SP11>> $\\pm$ <<LAC_SP11_SD>>"]]),
] + __import__("conteudo_resultados").BLOCOS_RESULTADOS
