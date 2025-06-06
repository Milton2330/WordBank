# 🌍 Análise de Sustentabilidade Fiscal de Países em Desenvolvimento

Este projeto interativo, desenvolvido com *Streamlit, permite visualizar e comparar indicadores econômicos de sustentabilidade fiscal de países sul-americanos em desenvolvimento. Os dados são obtidos automaticamente da API do **Banco Mundial (World Bank)*.

## 📊 Funcionalidades

- Selecione *países* (Argentina, Brasil, Chile, Peru, Uruguai).
- Escolha entre diversos *indicadores fiscais*, como:
  - Despesa de consumo do governo (% do PIB)
  - Receita fiscal total
  - Dívida externa
  - Crédito doméstico ao setor privado
  - Espaço Fiscal (Z-score médio)
- Filtre por *intervalos de anos* (1990 a 2024).
- Visualize gráficos estilizados com *matplotlib* e *interface amigável via Streamlit*.

## 🧠 Indicador Especial: Espaço Fiscal

O "Espaço Fiscal" é calculado com base em quatro indicadores normalizados (Z-score) e ponderados, considerando o impacto positivo ou negativo sobre a capacidade de endividamento dos países.

## 📦 Bibliotecas utilizadas

- streamlit
- wbgapi
- pandas
- matplotlib

> Veja o arquivo requirements.txt para versões exatas.

## ▶ Como executar

1. *Clone o repositório:*

```bash
git clone https://github.com/seuusuario/seuprojeto.git
cd seuprojeto