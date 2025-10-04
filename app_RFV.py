
# app_RFV.py - versão final pronta para deploy
import os
from io import BytesIO
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Análise RFV de Clientes")

# --- File uploader (fora de funções cacheadas) ---
uploaded = st.sidebar.file_uploader("Bank marketing data", type=['csv','xlsx'])

# --- Função de leitura (recebe uploaded) ---
@st.cache_data
def carregar_dados(data_file):
    """
    Lê o arquivo enviado se houver, senão carrega o CSV de fallback em data/.
    Retorna um DataFrame já com DiaCompra como datetime.
    """
    try:
        if data_file is not None:
            # UploadedFile ou caminho
            df = pd.read_csv(data_file, infer_datetime_format=True, parse_dates=['DiaCompra'])
        else:
            df = pd.read_csv('data/dados_input1_clean.csv', infer_datetime_format=True, parse_dates=['DiaCompra'])
    except Exception as e:
        st.error(f"Erro ao ler os dados: {e}")
        return None
    return df

# --- Função segura para qcut ---
def safe_qcut(series, q=4, labels=None):
    """
    Tenta pd.qcut; se falhar por bordas duplicadas, tenta com duplicates='drop'.
    Se ainda assim houver menos bins do que q, cria cortes sobre o rank da série.
    Retorna série (categoric/labels) ou NA se não for possível.
    """
    s = series.copy()
    if s.dropna().shape[0] == 0:
        return pd.Series([pd.NA] * len(s), index=s.index)
    try:
        return pd.qcut(s, q, labels=labels, duplicates='raise')
    except Exception:
        try:
            res = pd.qcut(s, q, labels=labels, duplicates='drop')
            if getattr(res, "cat", None) is not None and res.cat.categories.size < q:
                raise ValueError("Poucas categorias após duplicates='drop'")
            return res
        except Exception:
            ranks = s.rank(method='average', pct=False)
            try:
                return pd.cut(ranks, q, labels=labels)
            except Exception:
                return pd.Series([pd.NA] * len(s), index=s.index)

# --- Função para gerar Excel para download (exporta somente colunas RFV desejadas) ---
def gerar_excel(df_rfv):
    output = BytesIO()
    # Selecionar e ordenar colunas desejadas
    cols = ['ID_cliente', 'Recencia', 'Frequencia', 'Valor', 'R_quartil', 'F_quartil', 'V_quartil', 'RFV_Score']
    df_out = df_rfv.loc[:, cols].copy()
    # Ajuste de formatação (opcional): garantir tipos corretos
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_out.to_excel(writer, index=False, sheet_name='RFV')
    return output.getvalue()

# --- Carregar dados ---
df_compras = carregar_dados(uploaded)

if df_compras is None:
    st.warning("Nenhum dado carregado. Faça upload ou garanta que 'data/dados_input1_clean.csv' exista.")
else:
    st.subheader("Visualização inicial dos dados")
    st.dataframe(df_compras.head())

    # ---- Adaptação das colunas (assumimos: ID_cliente, CodigoCompra, DiaCompra, ValorTotal) ----
    try:
        df_compras['DiaCompra'] = pd.to_datetime(df_compras['DiaCompra'])
    except Exception as e:
        st.error("Erro ao converter 'DiaCompra' para datetime: " + str(e))
        st.stop()

    ultima_data = df_compras['DiaCompra'].max()

    recencia_df = df_compras.groupby('ID_cliente', as_index=False)['DiaCompra'].max()
    recencia_df['Recencia'] = (ultima_data - recencia_df['DiaCompra']).dt.days

    frequencia_df = df_compras.groupby('ID_cliente', as_index=False)['CodigoCompra'].count()
    frequencia_df.rename(columns={'CodigoCompra': 'Frequencia'}, inplace=True)

    valor_df = df_compras.groupby('ID_cliente', as_index=False)['ValorTotal'].sum()
    valor_df.rename(columns={'ValorTotal': 'Valor'}, inplace=True)

    df_rfv = recencia_df.merge(frequencia_df, on='ID_cliente').merge(valor_df, on='ID_cliente')

    # Quartis RFV com safe_qcut
    labels_R = [4, 3, 2, 1]     # R: menor recencia -> melhor etiqueta 4 (ajuste se preferir outro mapeamento)
    labels_FV = [1, 2, 3, 4]    # F e V: menor->1, maior->4

    df_rfv['R_quartil'] = safe_qcut(df_rfv['Recencia'], 4, labels=labels_R)
    df_rfv['F_quartil'] = safe_qcut(df_rfv['Frequencia'], 4, labels=labels_FV)
    df_rfv['V_quartil'] = safe_qcut(df_rfv['Valor'], 4, labels=labels_FV)

    # Forçar strings para concatenar e evitar categorias estranhas
    df_rfv['R_quartil'] = df_rfv['R_quartil'].astype(str)
    df_rfv['F_quartil'] = df_rfv['F_quartil'].astype(str)
    df_rfv['V_quartil'] = df_rfv['V_quartil'].astype(str)

    df_rfv['RFV_Score'] = df_rfv['R_quartil'] + df_rfv['F_quartil'] + df_rfv['V_quartil']

    st.subheader("Tabela RFV completa")
    st.dataframe(df_rfv)

    # Botão de download (exporta apenas as colunas RFV, sem DiaCompra)
    st.download_button(
        label="📥 Download Excel",
        data=gerar_excel(df_rfv),
        file_name='RFV_clientes.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    st.success("Se o download não iniciar automaticamente, verifique a pasta de downloads do seu navegador.")


    










