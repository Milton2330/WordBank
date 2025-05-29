import streamlit as st
import wbgapi as wb
import pandas as pd
import matplotlib.pyplot as plt



# Configurações gerais
plt.style.use('dark_background')
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['axes.titlepad'] = 20

# Países e indicadores (somente os do seu código novo)
PAISES = {
    'Argentina': 'ARG',
    'Brasil': 'BRA',
    'Chile': 'CHL',
    'Peru': 'PER',
    'Uruguai': 'URY'
}

INDICADORES = {
    'Dívida bruta geral do governo': 'GC.DOD.TOTL.GD.ZS',
    'Receita fiscal total': 'GC.TAX.TOTL.GD.ZS',
    'Estoques totais de dívida externa (USD)': 'DT.DOD.DECT.CD',
    'Crédito doméstico ao setor privado (% do PIB)': 'FS.AST.PRVT.GD.ZS',
    'PIB nominal (USD)': 'NY.GDP.MKTP.CD'
}

# Indicadores que impactam negativamente no espaço fiscal
INDICADORES_NEGATIVOS = ['GC.DOD.TOTL.GD.ZS', 'DT.DOD.DECT.CD']

# Cores
CORES = ['#ff595e', '#1982c4', '#6a4c93', '#8ac926', '#ffca3a']

# Anos permitidos
ANOS_COMPLETOS = list(range(1990, 2025))  # 1990 até 2024

####################
# FUNÇÕES UTILITÁRIAS
####################

def fetch_data(indicador_id, paises_codigos, anos):
    """
    Busca dados do indicador para os países e anos especificados.
    Retorna um DataFrame com índice anos e colunas países.
    """
    df = wb.data.DataFrame(indicador_id, paises_codigos, time=anos)
    # Transpõe para anos no índice e países nas colunas
    df = df.T
    # O índice agora são anos como string, converte para int
    df.index = df.index.str.replace('YR', '').astype(int)
    # Reindexa para garantir todos os anos selecionados
    df = df.reindex(anos)
    return df
fetch_data('GC.DOD.TOTL.GD.ZS', 'BRA', ANOS_COMPLETOS)

def plot_indicador(df, paises_selecionados, anos, titulo, sufixo_valor='%'):
    """
    Plota o gráfico do indicador com o dataframe df, países e anos.
    Não preenche valores faltantes para deixar buracos no gráfico.
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor('#121212')
    ax.set_facecolor('#1e1e1e')

    for i, pais in enumerate(paises_selecionados):
        if pais in df.columns:
            valores = df[pais].values  # mantém NaN onde não há dados
            cor = CORES[i % len(CORES)]
            ax.plot(anos, valores, color=cor, linewidth=2.5, label=pais)
            ax.fill_between(anos, valores, color=cor, alpha=0.3)
            # Só desenha o ponto e texto se o último valor não for NaN
            if len(valores) > 0 and pd.notna(valores[-1]):
                ax.scatter(anos[-1], valores[-1], color=cor, edgecolors='white', zorder=5)
                ax.text(anos[-1], valores[-1], f'{valores[-1]:.2f}{sufixo_valor}',
                        ha='left', va='center',
                        color='white', fontsize=10,
                        bbox=dict(facecolor=cor, alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2'))

    ax.set_title(titulo, fontsize=20, color='white', pad=25)
    ax.set_xlabel('Ano', fontsize=14, color='white')
    ax.set_ylabel(titulo, fontsize=14, color='white')
    ax.set_xticks(anos)
    ax.set_xlim(min(anos)-0.5, max(anos)+0.5)
    ax.tick_params(colors='white', labelsize=11)
    ax.grid(axis='both', color='gray', linestyle='--', linewidth=0.5, alpha=0.3)

    legend = ax.legend(framealpha=0.3, loc='upper left', fontsize=12)
    for text in legend.get_texts():
        text.set_color('white')

    st.pyplot(fig)


def calcula_espaco_fiscal(paises_codigos, anos):
    """
    Calcula o índice composto de espaço fiscal conforme seu código.
    Retorna df_media com z-score médio normalizado.
    """
    indicadores = list(INDICADORES.values())
    indicadores_negativos = INDICADORES_NEGATIVOS

    resultados = {}

    anos_df = [f'YR{ano}' for ano in anos]

    for ind in indicadores:
        df_indicador = wb.data.DataFrame(ind, paises_codigos, time=anos)
        df_indicador = df_indicador.reset_index()
        resultados[ind] = df_indicador
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

    for ind in indicadores:
        df = resultados[ind].copy()
        df.set_index('economy', inplace=True)
        if ind in indicadores_negativos:
            df = -df
        df = df.fillna(0)
        dfs_ajustados.append(df)

    df_soma = dfs_ajustados[0].copy()
    for df in dfs_ajustados[1:]:
        df_soma += df

    df_media = df_soma / len(indicadores)
    df_media = df_media.reset_index()

    return df_media

def plot_espaco_fiscal(df_media, paises_dict, anos_plot):
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor('#121212')
    ax.set_facecolor('#1e1e1e')

    df_plot = df_media.set_index('economy').T
    df_plot.index = [int(ano.replace('YR', '')) for ano in df_plot.index]
    df_plot = df_plot.loc[anos_plot]

    for i, (nome, codigo) in enumerate(paises_dict.items()):
        if codigo in df_plot.columns:
            valores = df_plot[codigo].fillna(0).values
            cor = CORES[i % len(CORES)]

            ax.plot(anos_plot, valores, color=cor, linewidth=2.5, label=nome, linestyle='-')
            ax.fill_between(anos_plot, valores, color=cor, alpha=0.15)
            if len(valores) > 0:
                ax.scatter(anos_plot[-1], valores[-1], color=cor, edgecolors='white', zorder=5)
                ax.text(anos_plot[-1], valores[-1], f'{valores[-1]:.2f}', ha='left', va='center',
                        color='white', fontsize=10,
                        bbox=dict(facecolor=cor, alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2'))

    ax.set_title('Espaço Fiscal - Z-score Médio', fontsize=20, color='white', pad=25)
    ax.set_xlabel('Ano', fontsize=14, color='white')
    ax.set_ylabel('Z-score médio ajustado', fontsize=14, color='white')
    ax.set_xticks(anos_plot)
    ax.tick_params(colors='white', labelsize=11)
    ax.grid(axis='both', color='gray', linestyle='--', linewidth=0.5, alpha=0.3)

    legend = ax.legend(framealpha=0.5, loc='upper left', fontsize=12)
    legend.get_frame().set_facecolor('#1e1e1e')
    legend.get_frame().set_edgecolor('gray')
    for text in legend.get_texts():
        text.set_color('white')

    plt.tight_layout()
    st.pyplot(fig)

##############
# STREAMLIT APP
##############
st.set_page_config(page_title='Dashboard Econômico', layout='wide')

st.title('Dashboard Econômico - Espaço Fiscal e Indicadores Individuais')

# Menu lateral para selecionar aba
aba = st.sidebar.radio('Selecione a aba:', ['Espaço Fiscal', 'Indicadores Individuais'])

if aba == 'Espaço Fiscal':
    st.sidebar.markdown('### Parâmetros Espaço Fiscal')
    anos_selecionados = st.sidebar.slider(
        'Selecione intervalo de anos:',
        min_value=1990, max_value=2024, value=(2000, 2024)
    )
    anos_espaco = list(range(anos_selecionados[0], anos_selecionados[1] + 1))

    paises_selecionados = st.sidebar.multiselect(
        'Selecione os países:', options=list(PAISES.keys()), default=list(PAISES.keys())
    )
    codigos_selecionados = [PAISES[p] for p in paises_selecionados]

    with st.spinner('Calculando espaço fiscal...'):
        df_media = calcula_espaco_fiscal(codigos_selecionados, anos_espaco)
        plot_espaco_fiscal(df_media, {p: PAISES[p] for p in paises_selecionados}, anos_espaco)

elif aba == 'Indicadores Individuais':
    st.sidebar.markdown('### Parâmetros Indicadores Individuais')
    indicador_selecionado = st.sidebar.selectbox('Selecione o indicador:', list(INDICADORES.keys()))
    anos_selecionados = st.sidebar.slider(
        'Selecione intervalo de anos:',
        min_value=1990, max_value=2024, value=(2000, 2024)
    )
    anos_indicador = list(range(anos_selecionados[0], anos_selecionados[1] + 1))

    paises_selecionados = st.sidebar.multiselect(
        'Selecione os países:', options=list(PAISES.keys()), default=list(PAISES.keys())
    )
    codigos_selecionados = [PAISES[p] for p in paises_selecionados]

    indicador_id = INDICADORES[indicador_selecionado]

    with st.spinner('Buscando dados do indicador...'):
        df_indicador = fetch_data(indicador_id, codigos_selecionados, anos_indicador)

    # plot_indicador(df_indicador, paises_selecionados, anos_indicador, indicador_selecionado)
    plot_indicador(df_indicador, paises_selecionados, anos_indicador, indicador_selecionado, sufixo_valor='%')