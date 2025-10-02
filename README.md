# Projeto Análise de Clientes

Este projeto é um **app Streamlit** que realiza a **segmentação de clientes usando RFV** (Recência, Frequência e Valor).  

Ele permite analisar o comportamento de compra dos clientes e criar ações de marketing/CRM direcionadas com base nos clusters formados.

---

## Funcionalidades

- Calcular **Recência (R)**: dias desde a última compra.  
- Calcular **Frequência (F)**: total de compras realizadas.  
- Calcular **Valor (V)**: total gasto no período.  
- Criar a tabela **RFV final** com classificação em quartis: A, B, C, D.  
- Sugerir **ações de marketing/CRM** de acordo com o perfil do cliente.  
- **Download** do resultado em Excel.

---

## Como usar

1. Certifique-se de ter o **Python 3.12** instalado.  
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt


3. Execute o app Streamlit:
   ```bash
   streamlit run app_RFV.py
   
Na barra lateral, suba o arquivo CSV (dados_input1.csv).
Visualize as tabelas e segmentos de clientes.
Baixe o resultado em Excel se desejar.


Requisitos :

Python 3.12
Streamlit
Pandas
Numpy
XlsxWriter
Pillow


Observações :

O app utiliza quartis para segmentar os clientes, sendo que:

Melhor quartil: A
Segundo melhor: B
Terceiro: C
Pior: D

A segmentação ajuda a criar estratégias de marketing direcionadas e retenção de clientes.
