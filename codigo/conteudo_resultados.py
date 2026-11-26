"""Seções 5 (continuação), 6 e declaração de IA. Ver marcações em conteudo.py."""

BLOCOS_RESULTADOS = [
("fig", "fig:box", "fig_boxplot",
 "Distribuição do hipervolume (à esquerda) e do número de soluções não dominadas "
 "(à direita) nas 30 repetições.", 0.74),
("p", "Com o mesmo orçamento de avaliações, o NSGA-II foi muito superior à soma ponderada: "
      "hipervolume médio de <<HV_NS>>, contra <<HV_SPT>> da SP-total ($p = <<P_SPT_HV>>$). "
      "A SP-total reinicia a busca para cada peso e dispõe de apenas 45 gerações por "
      "execução, insuficientes para organizar rotas de 50 clientes, enquanto o NSGA-II usa "
      "uma única população, em que boas sequências de clientes encontradas para uma região "
      "da frente são aproveitadas, por cruzamento, nas demais. A Figura {ref:fig:conv} "
      "mostra que o NSGA-II supera o hipervolume final da SP-total antes de 10.000 "
      "avaliações, menos de um quinto do orçamento."),
("fig", "fig:conv", "fig_convergencia",
 "Hipervolume da população do NSGA-II ao longo das avaliações (média e desvio padrão em "
 "30 repetições) e valores finais médios da soma ponderada.", 0.68),
("p", "Com onze vezes mais avaliações, a SP-11x obteve hipervolume ligeiramente maior que "
      "o do NSGA-II (<<HV_SP11>>, diferença de cerca de 0,03; $p = <<P_SP11_HV>>$). A "
      "vantagem se concentra no extremo de menor custo: a execução com $w = 1$ dedica "
      "50.000 avaliações a um só compromisso e encontra rotas de um veículo mais curtas "
      "(custo mínimo médio de {real}<<CMIN_SP11>>, contra {real}<<CMIN_NS>>). No extremo "
      "oposto, o NSGA-II alcançou tempos menores (<<TMIN_NS>> h contra <<TMIN_SP11>> h). "
      "Como a curva da Figura {ref:fig:conv} ainda cresce ao final, um orçamento maior "
      "provavelmente reduziria essa diferença, hipótese não testada aqui."),
("p", "A diferença mais marcante está no número de alternativas: o NSGA-II entregou em "
      "média <<N_NS>> soluções não dominadas por execução, cerca de <<RAZ_N>> vezes mais "
      "que a SP-11x ($p = <<P_SP11_N>>$), que, por construção, guarda uma solução por peso "
      "e nunca passa de 11; parte dessa diferença vem, portanto, do próprio desenho da "
      "comparação. A maior "
      "lacuna, porém, não diferiu de forma significativa ($p = <<P_SP11_LAC>>$): as frentes "
      "do NSGA-II são densas na região central, mas, em algumas repetições, não chegam ao "
      "extremo de menor custo, o que explica a alta variabilidade dessa métrica."),
("sub", "Frente de Pareto obtida", "sec:frente"),
("p", "A Figura {ref:fig:frentes} mostra a frente do NSGA-II na repetição de hipervolume "
      "mediano (semente <<SEED_MED>>, <<N_MED>> soluções) e as soluções da soma ponderada na "
      "mesma repetição. Partindo da solução mais barata, pequenos aumentos de custo trazem "
      "grandes reduções do tempo médio, até um ponto a partir do qual cada hora economizada "
      "custa muito mais. As soluções da SP-11x ficam próximas da frente, mas espaçadas e por "
      "vezes agrupadas em torno dos mesmos valores, como previsto por @das1997 para pesos "
      "uniformes; as da SP-total ficam longe dela."),
("fig", "fig:frentes", "fig_frentes",
 "Frente do NSGA-II na execução de hipervolume mediano e soluções da soma ponderada na "
 "mesma repetição. As linhas pontilhadas marcam o orçamento e o prazo do gestor; (a), (b) "
 "e (c) são as soluções escolhidas.", 0.74),
("p", "Um resultado que reforça o argumento do tema é a proporção de soluções *suportadas*, "
      "isto é, que minimizam alguma soma ponderada. Calculada com 2.001 pesos dentro da "
      "própria frente, ela foi de apenas <<SUP_NS>>% nas frentes do NSGA-II. Essa frente, "
      "porém, é uma aproximação: em média, <<DOM_NS>>% de suas soluções são dominadas por "
      "alguma solução da SP-11x na mesma repetição. Tomando como referência a união das "
      "frentes das três abordagens, <<NSUP_U>>% das soluções do NSGA-II continuam não "
      "dominadas e não são suportadas: estão em trechos não convexos da melhor frente "
      "conhecida e, se pertencerem à frente ótima, não seriam devolvidas por nenhuma "
      "escolha de pesos, por mais execuções que se fizessem [@das1997]. Elas não são "
      "necessariamente melhores, mas ficam invisíveis para quem usa apenas a soma "
      "ponderada."),
("sub", "Escolha da solução pelo gestor", "sec:gestor"),
("p", "Com a frente em mãos, a decisão deixa de ser a escolha prévia de pesos abstratos e "
      "passa a ser a escolha entre opções concretas (Tabela {ref:tab:gestor}). Com teto de "
      "{real}<<ORC>>,00 por dia (regra a), o gestor obtém tempo médio de <<OR_T>> h com "
      "<<OR_V>> veículos. Exigindo prazo médio de até <<PRAZO>> h (regra b), a solução mais "
      "barata usa <<PZ_V>> veículos e custa {real}<<PZ_C>>. O ponto de joelho (regra c), "
      "com <<JO_V>> veículos, reduz o tempo médio em <<JO_DT_PCT>>% em relação à solução mais "
      "barata, com aumento de custo de <<JO_DC_PCT>>%; a partir dele, chegar ao tempo mínimo "
      "exige custo <<MT_DC_PCT>>% maior para reduzir o tempo em mais <<MT_DT_PCT>>%. "
      "Esses percentuais tomam como referência o extremo de menor custo do NSGA-II, que, "
      "nessa repetição, é dominado pela solução mais barata da SP-11x ({real}<<SP11_MC_C>>; "
      "<<SP11_MC_T>> h), coerente com a vantagem da soma ponderada nesse extremo discutida "
      "na Seção {ref:sec:quant}."),
("tab", "tab:gestor", "Soluções da frente mediana do NSGA-II selecionadas por regra de "
        "decisão.", "lcccc",
 ["Regra", "Custo ({real}/dia)", "Tempo médio (h)", "Distância (km)", "Veículos"],
 [["Extremo: menor custo", "<<MC_C>>", "<<MC_T>>", "<<MC_KM>>", "<<MC_V>>"],
  ["(a) Orçamento $\\le$ {real}<<ORC>>", "<<OR_C>>", "<<OR_T>>", "<<OR_KM>>", "<<OR_V>>"],
  ["(b) Prazo $\\le$ <<PRAZO>> h", "<<PZ_C>>", "<<PZ_T>>", "<<PZ_KM>>", "<<PZ_V>>"],
  ["(c) Ponto de joelho", "<<JO_C>>", "<<JO_T>>", "<<JO_KM>>", "<<JO_V>>"],
  ["Extremo: menor tempo", "<<MT_C>>", "<<MT_T>>", "<<MT_KM>>", "<<MT_V>>"]]),
("p", "A Figura {ref:fig:rotas} ajuda a interpretar esses números. Entre um e cinco "
      "veículos, a distância total cresce pouco (de <<MC_KM>> km para <<PZ_KM>> km), porque "
      "as rotas passam a cobrir setores da região; o aumento de custo vem quase todo do custo "
      "fixo. Com oito veículos, as rotas ficam radiais, com muitas idas e voltas ao depósito, "
      "e a distância salta para <<MT_KM>> km. A figura também mostra cruzamentos de arestas "
      "na solução de menor custo, sinal de que esse extremo não foi totalmente otimizado, "
      "coerente com a vantagem da SP-11x nele."),
("fig", "fig:rotas", "fig_rotas",
 "Rotas de três soluções da frente mediana. O quadrado é o depósito e cada estilo de "
 "linha representa um veículo.", 1.0),
("sub", "Discussão e limitações", "sec:disc"),
("p", "A soma ponderada continua útil quando o decisor já conhece a importância relativa "
      "de custo e prazo; quando não conhece, a frente de Pareto torna explícito o preço de "
      "cada hora de antecipação. O estudo, porém, tem limitações: a instância é única, "
      "sintética e sem restrições de capacidade ou janelas de tempo, presentes na maioria "
      "das operações reais [@toth2014]; custos e velocidade são ilustrativos; os parâmetros "
      "não foram ajustados sistematicamente; a soma ponderada usou um único otimizador e "
      "guardou apenas uma solução por peso; e o "
      "NSGA-II foi aplicado sem busca local, que costuma ser decisiva em roteamento "
      "[@potvin2009]."),

# ============================================================ 6. CONCLUSÃO
("sec", "Conclusão e Trabalhos Futuros", "sec:conc"),
("p", "Este trabalho aplicou o NSGA-II a um problema sintético de roteamento com dois "
      "objetivos conflitantes, custo diário e tempo médio de entrega, e o comparou com a "
      "soma ponderada em 30 repetições. Com o mesmo orçamento, o NSGA-II obteve hipervolume "
      "de <<HV_NS>>, contra <<HV_SPT>>. Com onze vezes mais avaliações, a soma ponderada "
      "chegou a <<HV_SP11>>, mas ofereceu em média <<N_SP11>> alternativas, contra <<N_NS>> "
      "do NSGA-II, das quais, em média, <<NSUP_U>>% continuam não dominadas diante das "
      "três abordagens e não são suportadas, ficando fora do alcance de qualquer combinação "
      "de pesos sobre a melhor frente conhecida. A frente permitiu escolher soluções por orçamento, por prazo e "
      "pelo ponto de joelho, mostrando ao gestor, em reais e em horas, o que se ganha e o "
      "que se perde em cada escolha."),
("p", "Como trabalhos futuros, sugere-se: (i) incluir capacidade e janelas de tempo, com "
      "instâncias de referência da literatura; (ii) acrescentar busca local 2-opt ao "
      "NSGA-II para melhorar os extremos da frente; (iii) testar orçamentos maiores e outros "
      "algoritmos multiobjetivo; e (iv) aplicar o método a dados reais de uma operação de "
      "entregas."),

# ============================================================ IA
("secnn", "Declaração de Uso de Inteligência Artificial"),
("p", "Em conformidade com a Portaria CNPq nº 2.664/2026 e o Art. 12º do Manual de Normas "
      "de TCC da Universidade Tiradentes, os autores declaram que utilizaram a ferramenta "
      "de IA generativa Claude (Anthropic, modelo Claude Opus 5.5) nas seguintes etapas e "
      "finalidades: (i) *levantamento bibliográfico*, para localizar e conferir os dados "
      "bibliográficos das referências, todas verificadas nas fontes originais; (ii) "
      "*geração de código-fonte*, para escrever a primeira versão dos scripts do "
      "experimento, da análise estatística, das figuras e da verificação das tabelas, "
      "disponíveis no repositório indicado na Seção {ref:sec:impl}; (iii) *redação "
      "preliminar*, para produzir um rascunho das seções do artigo, posteriormente revisado "
      "e ajustado pelos autores; (iv) *tradução* do Resumo e das palavras-chave para o "
      "inglês; e (v) *execução do experimento*, cujos scripts foram executados no ambiente "
      "da ferramenta, conforme a Seção {ref:sec:impl}. A ferramenta não foi usada para "
      "inventar ou estimar dados: todos os valores das tabelas e figuras resultam da "
      "execução do código e podem ser reproduzidos a partir do repositório. A autoria e a responsabilidade integral pelo "
      "conteúdo do trabalho permanecem dos autores."),
]
