
   # Análise RFV de Clientes

Aplicação Streamlit que calcula Recência, Frequência e Valor (RFV) por cliente e gera segmentação em quartis.

URL pública da aplicação:
https://analise-clientes.onrender.com

## Como usar
1. Abra a aplicação no link acima.
2. No menu lateral, envie um arquivo CSV com as colunas **ID_cliente**, **CodigoCompra**, **DiaCompra** e **ValorTotal**, ou deixe que a aplicação use o arquivo de fallback (`data/dados_input1_clean.csv`).
   - Formato esperado:
     - `ID_cliente` (identificador do cliente)
     - `CodigoCompra` (identificador da transação)
     - `DiaCompra` (data da compra, ex.: 2021-12-07)
     - `ValorTotal` (valor da compra)
3. A aplicação exibirá a tabela RFV e permitirá o download do resultado em Excel (`RFV_clientes.xlsx`).

## Observações
- O app gera 3 quartis (R_quartil, F_quartil, V_quartil) e um RFV_Score concatenando os três.
- O processamento lida com empates e casos de distribuição não uniforme usando uma função segura (`safe_qcut`).
