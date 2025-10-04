
# app_RFV.py - versão final adaptada (cole integralmente neste arquivo)

import os
from io import BytesIO
import streamlit as st
import pandas as pd

# ---------------- Debug (temporário) ----------------
st.set_page_config(layout="wide")
st.title("Debug: Verificando CSV de fallback (temporário)")

csv_path = "data/dados_input1_clean.csv"

if os.path.exists(csv_path):
    st.success(f"Arquivo encontrado: {csv_path}")
    try:
        df_debug = pd.read_csv(csv_path, infer_datetime_format=True, parse_dates=['DiaCompra'])
        st.write("Primeiras linhas do CSV para conferência:")
        st.dataframe(df_debug.head())
        st.write("Colunas do CSV:", df_debug.columns.tolist())
    except Exception as e:
        st.error("Erro ao ler CSV de fallback (debug): " + str(e))
        st.stop()
else:
    st.error(f"Arquivo NÃO encontrado: {csv_path}")
    st.stop()
# ---------------- Fim debug -------------------------


# ---------------- App principal ---------------------
st.title("Análise RFV de Clientes")

# --- File uploader (fora de funções cacheadas) ---
uploaded = st.sidebar.file_uploader("Bank marketing data", type=['csv','xlsx'])

# --- Função de leitura (recebe uploaded) ---
def carregar_dados(data_file):
    """
    Lê o arquivo enviado se houver, senão carrega o CSV de fallback em data/.
    Retorna um DataFrame já com DiaCompra como datetime.
    """
    try:
        if data_file is not None:
            # data_file pode ser um UploadedFile (file-like)
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
    Retorna série (categoric/labels).
    """
    # Se série for inteira/nan, preencher nulos antes (evita erros)
    s = series.copy()
    # if all NaN, return NaN series
    if s.dropna().shape[0] == 0:
        return pd.Series([pd.NA] * len(s), index=s.index)

    try:
        return pd.qcut(s, q, labels=labels, duplicates='raise')
    except Exception:
        try:
            res = pd.qcut(s, q, labels=labels, duplicates='drop')
            # se categorias < q, fallback para rank
            if getattr(res, "cat", None) is not None and res.cat.categories.size < q:
                raise ValueError("Poucas categorias após duplicates='drop'")
            return res
        except Exception:
            # fallback por rank -> garante sempre q bins
            ranks = s.rank(method='average', pct=False)
            # se ainda assim houver problemas, usar cut direto
            try:
                return pd.cut(ranks, q, labels=labels)
            except Exception:
                # por fim, devolve uma série vazia categórica
                return pd.Series([pd.NA] * len(s), index=s.index)

# --- Função para gerar Excel para download ---
def gerar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='RFV')
    processed_data = output.getvalue()
    return processed_data

# --- Carregar dados (usando uploader) ---
df_compras = carregar_dados(uploaded)

if df_compras is None:
    st.warning("Nenhum dado carregado. Faça upload ou garanta que 'data/dados_input1_clean.csv' exista.")
else:
    st.subheader("Visualização inicial dos dados")
    st.dataframe(df_compras.head())

    # ---- Adaptação das colunas (assumindo estrutura detectada no CSV) ----
    # Seu CSV tem: ID_cliente, CodigoCompra, DiaCompra, ValorTotal
    # Vamos calcular Recencia, Frequencia e Valor agregado por cliente.

    # Garantir tipos
    try:
        df_compras['DiaCompra'] = pd.to_datetime(df_compras['DiaCompra'])
    except Exception as e:
        st.error("Erro ao converter 'DiaCompra' para datetime: " + str(e))
        st.stop()

    # última data observada (ponto de referência para recência)
    ultima_data = df_compras['DiaCompra'].max()

    # Recência: dias desde a última compra por cliente
    recencia_df = df_compras.groupby('ID_cliente', as_index=False)['DiaCompra'].max()
    recencia_df['Recencia'] = (ultima_data - recencia_df['DiaCompra']).dt.days

    # Frequência: número de compras por cliente (contagem de CodigoCompra)
    frequencia_df = df_compras.groupby('ID_cliente', as_index=False)['CodigoCompra'].count()
    frequencia_df.rename(columns={'CodigoCompra': 'Frequencia'}, inplace=True)

    # Valor: soma de ValorTotal por cliente
    valor_df = df_compras.groupby('ID_cliente', as_index=False)['ValorTotal'].sum()
    valor_df.rename(columns={'ValorTotal': 'Valor'}, inplace=True)

    # Juntar tudo em df_rfv
    df_rfv = recencia_df.merge(frequencia_df, on='ID_cliente').merge(valor_df, on='ID_cliente')

    # Aplicar safe_qcut para criar quartis (R=4..1, F/V=1..4)
    labels_R = [4, 3, 2, 1]  # Recencia: menor dias => melhor R=4? ajuste conforme sua lógica
    labels_FV = [1, 2, 3, 4]

    df_rfv['R_quartil'] = safe_qcut(df_rfv['Recencia'], 4, labels=labels_R)
    df_rfv['F_quartil'] = safe_qcut(df_rfv['Frequencia'], 4, labels=labels_FV)
    df_rfv['V_quartil'] = safe_qcut(df_rfv['Valor'], 4, labels=labels_FV)

    # Garantir strings (para concatenar)
    df_rfv['R_quartil'] = df_rfv['R_quartil'].astype(str)
    df_rfv['F_quartil'] = df_rfv['F_quartil'].astype(str)
    df_rfv['V_quartil'] = df_rfv['V_quartil'].astype(str)

    df_rfv['RFV_Score'] = df_rfv['R_quartil'] + df_rfv['F_quartil'] + df_rfv['V_quartil']

    # Mostrar tabela resultante
    st.subheader("Tabela RFV completa")
    st.dataframe(df_rfv)

    # Botão de download
    st.download_button(
        label="📥 Download Excel",
        data=gerar_excel(df_rfv),
        file_name='RFV_clientes.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    st.success("Se o download não começar, verifique seu navegador/tempo de deploy e tente novamente.")
# ---------------- Fim do app --------------------------

    










