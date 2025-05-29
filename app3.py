import streamlit as st
import wbgapi as wb
import pandas as pd
import matplotlib.pyplot as plt

# Estilo geral
plt.style.use('dark_background')
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['axes.titlepad'] = 20

# Países e cores
paises = {
    'Argentina': 'ARG',
    'Brasil': 'BRA',
    'Chile': 'CHL',
    'Peru': 'PER',
    'Uruguai': 'URY'
}
colors = ["#59dbff", "#19c419", "#c51e1e", "#e46e1a", "#1e18d5"]

# Indicadores normais
indicadores = {
    'Dívida bruta geral do governo': ('GC.DOD.TOTL.GD.ZS', 'Percentual do PIB (%)', '%'),
    'Receita fiscal total': ('GC.TAX.TOTL.GD.ZS', 'Percentual do PIB (%)', '%'),
    'Estoques totais de dívida externa (em USD)': ('DT.DOD.DECT.CD', 'Valor absoluto (USD)', ''),
    'Crédito doméstico ao setor privado (% do PIB)': ('FS.AST.PRVT.GD.ZS', 'Percentual do PIB (%)', '%'),
    'PIB': ('NY.GDP.MKTP.CD', 'Valor nominal (USD)', '')
}

# Adiciona o indicador especial do Espaço Fiscal
indicadores['Espaço Fiscal (Z-score médio)'] = ('espaco_fiscal', '', '')

# Função para plotar os indicadores normais
def plot_indicador(titulo, indicador_id, legenda_y, sufixo_valor, paises_selecionados, anos_selecionados):
    dados = {}
    for nome_pais in paises_selecionados:
        codigo_pais = paises[nome_pais]
        df = wb.data.DataFrame(indicador_id, codigo_pais, time=anos_selecionados).transpose()
        df.index = df.index.str.replace('YR', '').astype(int)
        df = df.reindex(anos_selecionados)
        dados[nome_pais] = df[codigo_pais].fillna(0).values

    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor('#121212')

    for i, (nome_pais, valores) in enumerate(dados.items()):
        cor = colors[list(paises.keys()).index(nome_pais)]
        ax.plot(anos_selecionados, valores, color=cor, linewidth=2.5, label=nome_pais)
        ax.fill_between(anos_selecionados, valores, color=cor, alpha=0.3)
        for ano, valor in zip(anos_selecionados, valores):
            ax.text(ano, valor, f'{valor:.2f}{sufixo_valor}', ha='center', va='bottom',
                    color='white', fontsize=9,
                    bbox=dict(facecolor=cor, alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2'))

    ax.set_title(titulo, fontsize=18, color='white', pad=25)
    ax.set_xlabel('Ano', fontsize=14, labelpad=12)
    ax.set_ylabel(legenda_y, fontsize=14, labelpad=12)
    ax.set_xticks(anos_selecionados)
    ax.set_xlim(min(anos_selecionados) - 0.5, max(anos_selecionados) + 0.5)
    ax.grid(axis='both', color='gray', linestyle='--', linewidth=0.5, alpha=0.3)

    legend = ax.legend(framealpha=0.3, loc='upper left', fontsize=12)
    for text in legend.get_texts():
        text.set_color('white')

    plt.figtext(0.5, 0.01, f"Fonte: World Bank API | Indicador: {indicador_id}",
                ha="center", fontsize=10, color='gray')

    plt.tight_layout()
    return fig

# Função para calcular e plotar o espaço fiscal (Z-score médio)
def calcular_espaco_fiscal(paises_selecionados, anos_selecionados):
    codigos_paises = [paises[p] for p in paises_selecionados]

    indicadores_lista = ['GC.DOD.TOTL.GD.ZS',
                        'GC.TAX.TOTL.GD.ZS',
                        'DT.DOD.DECT.CD',
                        'FS.AST.PRVT.GD.ZS',
                        'NY.GDP.MKTP.CD']

    indicadores_negativos = ['GC.DOD.TOTL.GD.ZS', 'DT.DOD.DECT.CD']

    anos_df = [f'YR{ano}' for ano in anos_selecionados]

    resultados = {}

    for ind in indicadores_lista:
        df_indicador = wb.data.DataFrame(ind, codigos_paises, time=anos_selecionados)
        df_indicador = df_indicador.reset_index()
        df_numeros = df_indicador[anos_df]

        df_normalizado = df_numeros.copy()
        for col in df_numeros.columns:
            valores_col = df_numeros[col]
            media = valores_col.mean()
            dp = valores_col.std()
            if dp != 0:
                df_normalizado[col] = (valores_col - media) / dp
            else:
                df_normalizado[col] = 0

        df_normalizado.insert(0, 'economy', df_indicador['economy'])
        resultados[ind] = df_normalizado

    dfs_ajustados = []
    for ind in indicadores_lista:
        df = resultados[ind].copy()
        df.set_index('economy', inplace=True)
        if ind in indicadores_negativos:
            df = -df
        df = df.fillna(0)
        dfs_ajustados.append(df)

    df_soma = dfs_ajustados[0].copy()
    for df in dfs_ajustados[1:]:
        df_soma += df
    df_media = df_soma / len(indicadores_lista)
    df_media = df_media.reset_index()

    return df_media

def plot_zscore_media(df_media, paises_dict, anos_selecionados, titulo='Espaço Fiscal - Z-score Médio'):
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor('#121212')
    ax.set_facecolor('#1e1e1e')

    df_plot = df_media.set_index('economy').T
    df_plot.index = [int(ano.replace('YR', '')) for ano in df_plot.index]
    df_plot = df_plot.loc[anos_selecionados]

    for i, (nome, codigo) in enumerate(paises_dict.items()):
        if codigo in df_plot.columns:
            valores = df_plot[codigo].fillna(0).values
            cor = colors[i]

            ax.plot(anos_selecionados, valores, color=cor, linewidth=2.5, label=nome, linestyle='-')
            ax.fill_between(anos_selecionados, valores, color=cor, alpha=0.15)

            if len(valores) > 0:
                ax.scatter(anos_selecionados[-1], valores[-1], color=cor, edgecolors='white', zorder=5)
                ax.text(anos_selecionados[-1], valores[-1], f'{valores[-1]:.2f}', ha='left', va='center',
                        color='white', fontsize=10,
                        bbox=dict(facecolor=cor, alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2'))

    ax.set_title(titulo, fontsize=20, color='white', pad=25)
    ax.set_xlabel('Ano', fontsize=14, color='white')
    ax.set_ylabel('Z-score médio ajustado', fontsize=14, color='white')
    ax.set_xticks(anos_selecionados)
    ax.tick_params(colors='white', labelsize=11)
    ax.grid(axis='both', color='gray', linestyle='--', linewidth=0.5, alpha=0.3)

    legend = ax.legend(framealpha=0.5, loc='upper left', fontsize=12)
    legend.get_frame().set_facecolor('#1e1e1e')
    legend.get_frame().set_edgecolor('gray')
    for text in legend.get_texts():
        text.set_color('white')

    plt.figtext(0.5, 0.01, "Fonte: Média dos indicadores normalizados via World Bank API",
                ha="center", fontsize=10, color='gray')

    plt.tight_layout()
    return fig

# --- STREAMLIT ---

st.set_page_config(layout="wide")
st.title("CAPACIDADE DE PAGAMENTO DE EMPRÉSTIMOS POR PAÍSES EM DESENVOLVIMENTO")
st.markdown("### Uma análise de sustentabilidade fiscal frente aos financiamentos do Banco Mundial")
st.markdown("Selecione os países e um indicador no menu à esquerda para visualizar o gráfico.")

# Sidebar - seleção de países
paises_selecionados = st.sidebar.multiselect(
    "Selecione o(s) país(es):",
    options=list(paises.keys()),
    default=list(paises.keys())
)

if not paises_selecionados:
    st.sidebar.warning("Selecione pelo menos um país.")
    st.stop()

# Sidebar - seleção de anos com slider
ano_inicial, ano_final = st.sidebar.select_slider(
    "Selecione o intervalo de anos:",
    options=list(range(1990, 2025)),
    value=(1990, 2024)
)

anos_selecionados = list(range(ano_inicial, ano_final + 1))

# Sidebar - seleção do indicador
indicador_escolhido = st.sidebar.selectbox(
    "Selecione o indicador:",
    options=list(indicadores.keys())
)

# Mostrar gráfico conforme indicador
if indicador_escolhido == 'Espaço Fiscal (Z-score médio)':
    with st.spinner('Calculando Espaço Fiscal...'):
        df_media = calcular_espaco_fiscal(paises_selecionados, anos_selecionados)
        fig = plot_zscore_media(df_media, {p: paises[p] for p in paises_selecionados}, anos_selecionados)
        st.pyplot(fig)
else:
    codigo_indicador, legenda_y, sufixo = indicadores[indicador_escolhido]
    with st.spinner(f'Carregando dados para {indicador_escolhido}...'):
        fig = plot_indicador(indicador_escolhido, codigo_indicador, legenda_y, sufixo,
                            paises_selecionados, anos_selecionados)
        st.pyplot(fig)
