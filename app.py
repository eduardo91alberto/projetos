import streamlit as st
import pandas as pd
from datetime import date, timedelta

st.set_page_config(layout='wide', page_title='Point da Massa')

st.subheader('Analise de Compras - Point da Massa')

with st.container():
    col1, col2, col3 = st.columns([1,2.5,2.5]) 
    start_date = date.today().replace(day=1)
    end_date = (start_date.replace(month=start_date.month % 12 + 1, day=1) - timedelta(days=1))
    data_select = col1.date_input('Selecione o período', [start_date, end_date], format='DD/MM/YYYY')

url_compras = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRZzdqgnKHkLJ_7taLdMJtElFZRWucobAJ6CECJlpr6nau19X4s9fsgzNZ9ZRbGj6zvw8zfV5HmXjL_/pub?gid=0&single=true&output=csv'

df_compras = pd.read_csv(url_compras, sep=',')
df_compras = df_compras.loc[:,['Data da Compra',
                               'Produto',
                               'Quantidade',
                               'Unidade de Medida (KG, LITROS)',
                               'Custo Unitário (R$)',
                               'Custo Total (R$)',
                               'Forma de Pagamento']]
df_compras['Custo Total (R$)'] = df_compras['Custo Total (R$)'].str.replace('R\$','', regex=True).str.replace(',','.').astype(float)
df_compras['Custo Unitário (R$)'] = df_compras['Custo Unitário (R$)'].str.replace('R\$','', regex=True).str.replace(',','.').astype(float)
df_compras['Data da Compra'] = pd.to_datetime(df_compras['Data da Compra']).dt.date
df_compras['Quantidade'] = df_compras['Quantidade'].str.replace(',','.').astype(float)
df_compras = df_compras.dropna()

df_compras_periodo = df_compras[(df_compras['Data da Compra'] <= data_select[1]) & (df_compras['Data da Compra'] >= data_select[0])]
compra_total_perido = df_compras_periodo['Custo Total (R$)'].sum()

st.metric(label='Compra Total', value=f'R$ {compra_total_perido:,.2f}'.replace(',','-').replace('.',',').replace('-','.'))

compra_por_produto = df_compras_periodo.groupby('Produto')['Custo Total (R$)'].sum().reset_index()
compra_por_produto.sort_values(by='Custo Total (R$)', ascending=False, inplace=True, ignore_index=True)
compra_por_produto['Custo Total (R$)'] = compra_por_produto['Custo Total (R$)'].round(2)
compra_por_produto