
# =================== Bloco de Debug ===================
import os
import streamlit as st
import pandas as pd

st.title("Debug: Verificando CSV de fallback")

csv_path = "data/dados_input1_clean.csv"

if os.path.exists(csv_path):
    st.success(f"Arquivo encontrado: {csv_path}")
    st.write("Primeiras linhas do CSV para conferência:")
    df_debug = pd.read_csv(csv_path)
    st.dataframe(df_debug.head())
else:
    st.error(f"Arquivo NÃO encontrado: {csv_path}")
    st.stop()
# =================== Fim do Bloco de Debug ===================

from io import BytesIO

st.title("Análise RFV de Clientes")

# Função para leitura de CSV com fallback
@st.cache_data
def carregar_dados():
    data_file_1 = st.sidebar.file_uploader("Bank marketing data", type=['csv','xlsx'])
    if data_file_1 is not None:
        try:
            df = pd.read_csv(data_file_1, infer_datetime_format=True, parse_dates=['DiaCompra'])
        except Exception as e:
            st.error(f"Erro ao ler o arquivo enviado: {e}")
            return None
    else:
        try:
            df = pd.read_csv('data/dados_input1_clean.csv', infer_datetime_format=True, parse_dates=['DiaCompra'])
        except FileNotFoundError:
            st.warning("Nenhum arquivo enviado e 'dados_input1_clean.csv' não encontrado no repositório.")
            return None
    return df

# Função para gerar arquivo Excel para download
def gerar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='RFV')
    processed_data = output.getvalue()
    return processed_data

# Carregar dados
df_compras = carregar_dados()

if df_compras is not None:
    st.subheader("Visualização inicial dos dados")
    st.write(df_compras.head())

    # Cálculo dos quartis RFV
    df_compras['R_quartil'] = pd.qcut(df_compras['Recencia'], 4, labels=[4,3,2,1])
    df_compras['F_quartil'] = pd.qcut(df_compras['Frequencia'], 4, labels=[1,2,3,4])
    df_compras['V_quartil'] = pd.qcut(df_compras['Valor'], 4, labels=[1,2,3,4])
    df_compras['RFV_Score'] = df_compras['R_quartil'].astype(str) + df_compras['F_quartil'].astype(str) + df_compras['V_quartil'].astype(str)

    st.subheader("Tabela RFV completa")
    st.dataframe(df_compras)

    st.download_button(
        label="📥 Download Excel",
        data=gerar_excel(df_compras),
        file_name='RFV_clientes.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


    









