import streamlit as st
import pandas as pd
from datetime import date, timedelta

st.set_page_config(layout='wide', page_title='Point da Massa')

pagina = st.sidebar.radio('Selecione a Pagina', ['Compras','Vendas', 'Analise'])

# PAGINA DE COMPRAS
def pagina_compras():
    st.subheader('Analise de Compras - Point da Massa')

    #Planilha "De Para" - Produtos
    df_para_produto = pd.read_csv('produto_categorias.csv', sep=',')
    df_para_produto.rename(columns={
        'De':'Produto',
        'Para':'descricao_prod'
    }, inplace=True)

    lista_categorias = ['TODAS'] #Lista de Categorias - Segmentação
    for valor in df_para_produto['Categorias'].unique():
        lista_categorias.append(valor)

    with st.container():
        col1, col2, col3 = st.columns([1,2.5,2.5]) 
        start_date = date.today().replace(day=1)
        end_date = (start_date.replace(month=start_date.month % 12 + 1, day=1) - timedelta(days=1))
        data_select = st.sidebar.date_input('Selecione o período', [start_date, end_date], format='DD/MM/YYYY')
        filtro_categoria = col1.selectbox('Selecione a Categorias', lista_categorias)

    url_compras = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRZzdqgnKHkLJ_7taLdMJtElFZRWucobAJ6CECJlpr6nau19X4s9fsgzNZ9ZRbGj6zvw8zfV5HmXjL_/pub?gid=0&single=true&output=csv'

    df_compras = pd.read_csv(db_compras, sep=',')
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

    df_compras = pd.merge(df_compras, df_para_produto, on='Produto', how='left')
    df_compras = df_compras.dropna() # df compras geral

    def filtro_cat():
        if filtro_categoria == 'TODAS':
            return df_compras
        else:
            return df_compras[df_compras['Categorias'] == filtro_categoria]

    df_compras_periodo = filtro_cat()
    df_compras_periodo = df_compras_periodo[(df_compras_periodo['Data da Compra'] <= data_select[1]) & (df_compras_periodo['Data da Compra'] >= data_select[0])]
    compra_total_perido = df_compras_periodo['Custo Total (R$)'].sum()

    st.metric(label='Compra Total', value=f'R$ {compra_total_perido:,.2f}'.replace(',','-').replace('.',',').replace('-','.'))

    compra_por_produto = df_compras_periodo.groupby('Produto')['Custo Total (R$)'].sum().reset_index()
    compra_por_produto.sort_values(by='Custo Total (R$)', ascending=False, inplace=True, ignore_index=True)
    compra_por_produto['Custo Total (R$)'] = compra_por_produto['Custo Total (R$)'].round(2)

    #Tabela Resumo Categorias
    df_categorias = df_compras_periodo.groupby('Categorias')['Custo Total (R$)'].sum().reset_index()
    df_categorias['Part_%'] = df_categorias['Custo Total (R$)'] / df_categorias['Custo Total (R$)'].sum() * 100
    df_categorias['Part_%'] = df_categorias['Part_%'].round(2)

    #Tabela Resumo SubCategorias
    df_subcategorias = df_compras_periodo.groupby('Subcategoria')['Custo Total (R$)'].sum().reset_index()
    df_subcategorias['Part_%'] = df_subcategorias['Custo Total (R$)'] / df_subcategorias['Custo Total (R$)'].sum() * 100
    df_subcategorias['Part_%'] = df_subcategorias['Part_%'].round(2)

    with st.container():
        col1, col2, col3 = st.columns(3)
        col1.dataframe(df_categorias.sort_values(by='Custo Total (R$)', ascending=False), hide_index=True, height=250, width=500)
        col2.dataframe(df_subcategorias.sort_values(by='Custo Total (R$)', ascending=False), hide_index=True, height=250, width=500)
        col3.dataframe(compra_por_produto, hide_index=True, height=250, width=500)

# PAGINA DE VENDAS
def pagina_vendas():
    st.subheader('Analise de Vendas - Point da Massa')


if pagina == 'Compras':
    pagina_compras()
elif pagina == 'Vendas':
    pagina_vendas()
