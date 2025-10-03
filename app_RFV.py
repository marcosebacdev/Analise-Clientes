
# =================== Bloco de Debug ===================
import os
import streamlit as st
import pandas as pd

st.title("Debug: Verificando CSV de fallback")

# Caminho do CSV de fallback
csv_path = "data/dados_input1_clean.csv"

# Verificando se o arquivo existe
if os.path.exists(csv_path):
    st.success(f"Arquivo encontrado: {csv_path}")
    st.write("Primeiras linhas do CSV para conferência:")
    df_debug = pd.read_csv(csv_path)
    st.dataframe(df_debug.head())
    st.write("Colunas do CSV:", df_debug.columns.tolist())
else:
    st.error(f"Arquivo NÃO encontrado: {csv_path}")
    st.stop()  # Para o app aqui se o arquivo não existir

# =================== Fim do Bloco de Debug ===================

from io import BytesIO

# Título do app
st.title("Análise RFV de Clientes")

# Função para leitura de CSV com fallback
def carregar_dados():
    data_file_1 = st.sidebar.file_uploader("Bank marketing data", type=['csv','xlsx'])
    if data_file_1 is not None:
        try:
            df = pd.read_csv(data_file_1, infer_datetime_format=True, parse_dates=['DiaCompra'])
        except Exception as e:
            st.error(f"Erro ao ler o arquivo enviado: {e}")
            return None
    else:
        # fallback: carregar arquivo padrão do repositório dentro da pasta data
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
        writer.save()
    processed_data = output.getvalue()
    return processed_data

# Carregar dados
df_compras = carregar_dados()

if df_compras is not None:
    # MOSTRAR PRIMEIRAS LINHAS PARA TESTE
    st.subheader("Visualização inicial dos dados")
    st.write(df_compras.head())

    # ===== Cálculo RFV adaptado =====
    import datetime as dt

    # Recência: dias desde a última compra
    df_compras['DiaCompra'] = pd.to_datetime(df_compras['DiaCompra'])
    ultima_data = df_compras['DiaCompra'].max()
    recencia_df = df_compras.groupby('ID_cliente')['DiaCompra'].max().reset_index()
    recencia_df['Recencia'] = (ultima_data - recencia_df['DiaCompra']).dt.days

    # Frequência: número de compras
    frequencia_df = df_compras.groupby('ID_cliente')['CodigoCompra'].count().reset_index()
    frequencia_df.rename(columns={'CodigoCompra':'Frequencia'}, inplace=True)

    # Valor: total gasto
    valor_df = df_compras.groupby('ID_cliente')['ValorTotal'].sum().reset_index()
    valor_df.rename(columns={'ValorTotal':'Valor'}, inplace=True)

    # Juntar tudo
    df_rfv = recencia_df.merge(frequencia_df, on='ID_cliente').merge(valor_df, on='ID_cliente')

    # Quartis RFV
    df_rfv['R_quartil'] = pd.qcut(df_rfv['Recencia'], 4, labels=[4,3,2,1])
    df_rfv['F_quartil'] = pd.qcut(df_rfv['Frequencia'], 4, labels=[1,2,3,4])
    df_rfv['V_quartil'] = pd.qcut(df_rfv['Valor'], 4, labels=[1,2,3,4])
    df_rfv['RFV_Score'] = df_rfv['R_quartil'].astype(str) + df_rfv['F_quartil'].astype(str) + df_rfv['V_quartil'].astype(str)

    st.subheader("Tabela RFV completa")
    st.dataframe(df_rfv)

    # Botão de download
    st.download_button(
        label="📥 Download Excel",
        data=gerar_excel(df_rfv),
        file_name='RFV_clientes.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )










