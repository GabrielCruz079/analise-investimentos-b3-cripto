# 📈 Análise de Investimentos B3 + Cripto

Análise comparativa de retorno, risco e volatilidade de um portfólio simulado combinando ações da B3 e criptomoedas, com dados reais coletados via Yahoo Finance (2023–2024).

> ⚠️ Projeto de simulação para fins de estudo e portfólio. Não constitui recomendação de investimento.

---

## 🎯 Objetivo

Simular um portfólio de R$ 10.000 dividido entre 6 ações da B3 e 3 criptomoedas, medir o desempenho real de cada ativo no período, e construir um pipeline completo — coleta, tratamento, análise e visualização — do dado bruto ao dashboard executivo.

## 🛠️ Tecnologias

- **Python** (pandas, yfinance, matplotlib, seaborn) — coleta e tratamento de dados
- **MySQL** — armazenamento estruturado de preços históricos e indicadores
- **Excel** (openpyxl) — camada intermediária de exportação
- **Power BI** — dashboard executivo interativo

## 📁 Estrutura do repositório

├── coleta_acoes_b3.py # Coleta de preços via Yahoo Finance e cálculo de indicadores <BR>
├── eda_investimentos.py # EDA, geração de gráficos e exportação para Excel/Power BI <BR>
├── dados/ <BR>
│ └── investimentos_powerbi.xlsx
├── graficos/ # 7 gráficos gerados automaticamente <BR>
└── dashboard /<BR>
└── investimentos.pbix # Dashboard executivo no Power BI


## 📊 Principais resultados

| Ativo | Tipo | Retorno acumulado (2023–2024) |
|---|---|---|
| SOL-USD | Cripto | +1.813,69% |
| BTC-USD | Cripto | +457,25% |
| ETH-USD | Cripto | +179,47% |
| PETR4 | Ação | +57,9% |
| BBDC4 | Ação | -21,63% |
| AMER3 | Ação | -99,31% |

**Retorno total do portfólio simulado:** `[CONFERIR]`%
**Valor atual do portfólio (partindo de R$ 10.000):** R$ `[CONFERIR]`

### 🔎 Insight sobre o outlier AMER3

A ação AMER3 (Americanas) sofreu uma queda de praticamente -99% no período, resultado do escândalo contábil bilionário revelado em janeiro de 2023, que levou a empresa à recuperação judicial. Esse dado real ilustra risco de concentração e a importância de diversificação num portfólio.

## 🖼️ Visualizações

Os 7 gráficos gerados incluem: retorno acumulado por tipo de ativo, ranking comparativo de retorno, volatilidade média de 30 dias, evolução de preço normalizado (base 100), matriz de correlação entre ativos, risco x retorno, e composição/lucro do portfólio simulado.

## 📐 Metodologia

- Coleta via `yfinance`, com tickers da B3 ajustados para o sufixo `.SA` exigido pelo Yahoo Finance
- Retorno acumulado calculado como `(preço final − preço inicial) / preço inicial × 100`, usando o primeiro e o último preço de fechamento da série
- Volatilidade calculada como desvio-padrão móvel de 30 dias sobre o retorno diário

## 🚀 Como reproduzir

```bash
pip install yfinance pymysql pandas matplotlib seaborn openpyxl

# 1. Rodar a coleta (requer MySQL local configurado, ver seção de banco de dados)
python coleta_acoes_b3.py

# 2. Rodar a análise e exportar para Power BI
python eda_investimentos.py
```

Abra `dashboard/investimentos.pbix` no Power BI Desktop para o dashboard interativo.

## 👤 Autor

**Gabriel Ramos Cruz** — Analista de Dados em Formação
[LinkedIn](https://www.linkedin.com/in/gabriel-ramos-50a081357/) · [Portfólio](https://gabrielcruz079.github.io/)
