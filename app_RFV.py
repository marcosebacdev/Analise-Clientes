
import streamlit as st
import pandas as pd
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
        # fallback: carregar arquivo padrão do repositório
        try:
            df = pd.read_csv('dados_input1.csv', infer_datetime_format=True, parse_dates=['DiaCompra'])
        except FileNotFoundError:
            st.warning("Nenhum arquivo enviado e 'dados_input1.csv' não encontrado no repositório.")
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
    # Exemplo: criar colunas de quartis RFV (supondo que já tenha Recencia, Frequencia, Valor)
    df_compras['R_quartil'] = pd.qcut(df_compras['Recencia'], 4, labels=[4,3,2,1])
    df_compras['F_quartil'] = pd.qcut(df_compras['Frequencia'], 4, labels=[1,2,3,4])
    df_compras['V_quartil'] = pd.qcut(df_compras['Valor'], 4, labels=[1,2,3,4])
    df_compras['RFV_Score'] = df_compras['R_quartil'].astype(str) + df_compras['F_quartil'].astype(str) + df_compras['V_quartil'].astype(str)

    st.subheader("Tabela RFV")
    st.dataframe(df_compras)

    # Botão de download
    st.download_button(
        label="📥 Download Excel",
        data=gerar_excel(df_compras),
        file_name='RFV_clientes.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    









