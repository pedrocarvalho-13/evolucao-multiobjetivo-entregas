# Evolução multiobjetivo: custo e tempo de entrega ao mesmo tempo

Código, dados e artigo do trabalho do Tema 38 da disciplina de Machine Learning e Data Science —
Curso de Sistemas de Informação, Universidade Tiradentes (UNIT).

**Autores:** Enzo Figueiredo Feitosa, Mateus Henrique de Araújo Santos, Pedro Carvalho,
Luiz Henrique, Anthony Yuri Feitosa França e Guilherme Santos.

O sistema aplica o **NSGA-II** a um problema sintético de roteamento de entregas (50 clientes,
até 8 veículos) com dois objetivos conflitantes — **custo diário (R$)** e **tempo médio de
entrega (h)** — e compara a frente de Pareto obtida com o **método da soma ponderada**, em 30
repetições independentes.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `codigo/experimento.py` | Problema, NSGA-II e soma ponderada (SP-total e SP-11x); gera `resultados/execucoes.json` |
| `codigo/analise.py` | Hipervolume, testes de Mann-Whitney, escolha do gestor e figuras; gera `resultados/resumo.json` e `figuras/` |
| `codigo/verificar_tabelas.py` | Reconstrói as Tabelas 2 e 3 a partir dos dados brutos e confere cada valor com o `artigo.tex` |
| `codigo/gerar_artigo.py` | Gera `artigo.tex` e `artigo.docx` (modelo SBC) com os números de `resumo.json` |
| `codigo/conteudo.py`, `codigo/conteudo_resultados.py` | Texto do artigo (fonte única para o `.tex` e o `.docx`) |
| `codigo/referencias.py` | Referências bibliográficas |
| `codigo/modelo-tcc-sbc.docx` | Modelo SBC usado como base do `.docx` |
| `resultados/` | Dados brutos das 30 repetições, resumo das métricas e saída da verificação |
| `figuras/` | Figuras do artigo (PDF e PNG, em tons de cinza) |
| `artigo.docx` | O artigo (versão entregue, modelo SBC em Word) |
| `artigo.tex` | Mesmo artigo em LaTeX, gerado da mesma fonte |

## Como executar

Requer Python 3.10+ (testado em Python 3.13, no Linux e no Windows 11).

```bash
pip install -r requirements.txt
cd codigo
python experimento.py          # 30 repetições (~20 min em 2 núcleos); use --reps 5 para um teste rápido
python analise.py              # métricas, testes estatísticos e figuras
python verificar_tabelas.py    # reconstrói as tabelas e confere com o artigo
python gerar_artigo.py         # (opcional) regenera artigo.tex e artigo.docx
```

`verificar_tabelas.py` termina com `Conferência com artigo.tex: 20/20 valores idênticos.`
quando todos os valores das tabelas do artigo conferem com a execução.

## Parâmetros principais

Definidos no início de `codigo/experimento.py`: 50 clientes em um quadrado de 100 × 100 km
(semente 42), até 8 veículos, 40 km/h, 10 min de parada, R$ 250,00 de custo fixo por veículo e
R$ 2,50 por km; população de 100, 500 gerações, cruzamento OX (0,9) e mutação por inversão (0,6);
30 repetições com sementes 1 a 30.

## Uso de IA

A primeira versão do código e do texto foi produzida com apoio da ferramenta Claude (Anthropic),
conforme a declaração de uso de IA do artigo. Os resultados vêm exclusivamente da execução deste
código.
