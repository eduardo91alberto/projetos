import streamlit as st
import pandas as pd
from datetime import date, timedelta
import plotly.express as px

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

    compra_por_produto = df_compras_periodo.groupby('descricao_prod')['Custo Total (R$)'].sum().reset_index()
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

        col1.markdown('##### Resumo por Categorias')
        col1.dataframe(df_categorias.sort_values(by='Custo Total (R$)', ascending=False), hide_index=True, height=250, width=500)
        col2.markdown('##### Resumo por SubCategorias')
        col2.dataframe(df_subcategorias.sort_values(by='Custo Total (R$)', ascending=False), hide_index=True, height=250, width=500)
        col3.markdown('##### Resumo por Protudos')
        col3.dataframe(compra_por_produto.sort_values(by='Custo Total (R$)', ascending=False), hide_index=True, height=250, width=500)

    with st.container():
        col1, col2, col3 = st.columns([2,1,1])
        filtro_produto = col1.selectbox('Selecione o Produto', 
                                        compra_por_produto['descricao_prod'].unique())


    df_produto_filtrado = df_compras_periodo[df_compras_periodo['descricao_prod'] == filtro_produto]

    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        col3.metric(label='Qtd de Compras', value=df_produto_filtrado['Produto'].count())
        col2.metric(label='Volume Comprado', value=df_produto_filtrado['Quantidade'].sum().round(2))
        col1.metric(label='Compra Total', value=f'R$ {df_produto_filtrado['Custo Total (R$)'].sum():.2f}')

        preco_min = df_produto_filtrado['Custo Unitário (R$)'].min()
        preco_medio = df_produto_filtrado['Custo Unitário (R$)'].mean().round(2)
        variacao_mimxmed = preco_medio / preco_min - 1

        col4.metric(label='Preço Médio', 
                    value=f'R$ {df_produto_filtrado['Custo Unitário (R$)'].mean().round(2):.2f}', 
                    delta=f'{variacao_mimxmed:.2%}')


    
    # Grafico Historico de Produtos
    fig_1 = px.line(df_produto_filtrado, x='Data da Compra', y='Custo Unitário (R$)', title='Historico Valor de Compra',
                    markers=True, render_mode='svg', line_shape='spline', text='Custo Unitário (R$)',
                    height=300)
    fig_1.update_traces(textposition='top center')
    fig_1.update_layout(
        yaxis=dict(
            dtick=6  # Define o espaçamento entre as linhas do eixo Y
        ),
        yaxis_range=[df_produto_filtrado['Custo Unitário (R$)'].min() * 0.85, 
                     df_produto_filtrado['Custo Unitário (R$)'].max() * 1.15],

        xaxis_range=[df_produto_filtrado['Data da Compra'].min() - timedelta(days=1),
                     df_produto_filtrado['Data da Compra'].max() + timedelta(days=1)]
    )

    fig_1 # GRAGICO - Variação de Preços de Compra



# PAGINA DE VENDAS
def pagina_vendas():
    st.subheader('Analise de Vendas - Point da Massa')

    start_date = date.today().replace(day=1)
    end_date = (start_date.replace(month=start_date.month % 12 + 1, day=1) - timedelta(days=1))
    data_select = st.sidebar.date_input('Selecione o período', [start_date, end_date], format='DD/MM/YYYY')

    url_vendas = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRZzdqgnKHkLJ_7taLdMJtElFZRWucobAJ6CECJlpr6nau19X4s9fsgzNZ9ZRbGj6zvw8zfV5HmXjL_/pub?gid=2129777218&single=true&output=csv'
    
    df_vendas = pd.read_csv(url_vendas, sep=',')
    df_vendas = df_vendas.loc[:,['Data',
                                 'Canal de vendas (Salão, Delivery (IFOOD), Delivery (Whatsapp)',
                                 'Prato Vendido',
                                 'Adicionais',
                                 'Sobremesa',
                                 'Bebida',
                                 'Quantidade',
                                 'Preço Unitário (R$)',
                                 'Total da Venda (R$)']]
    
    df_vendas.rename(columns={
        'Canal de vendas (Salão, Delivery (IFOOD), Delivery (Whatsapp)':'Canal de Vendas'
    }, inplace=True)

    df_vendas['Total da Venda (R$)'] = df_vendas['Total da Venda (R$)'].str.replace('R\$','', regex=True).str.replace(',','.').astype(float)
    df_vendas['Preço Unitário (R$)'] = df_vendas['Preço Unitário (R$)'].str.replace('R\$','', regex=True).str.replace(',','.').astype(float)
    df_vendas['Data'] = pd.to_datetime(df_vendas['Data']).dt.date
    df_vendas = df_vendas.dropna(subset=['Data','Canal de Vendas'])

    df_vendas_filtrado = df_vendas[(df_vendas['Data'] <= data_select[1]) & (df_vendas['Data'] >= data_select[0])]

    with st.container():
        col1, col2, col3 = st.columns([1,2,2])

        lista_canal = ['Todos'] #Lista de Categorias - Segmentação
        for valor in df_vendas['Canal de Vendas'].unique():
            lista_canal.append(valor)
        filtro_canal = col1.selectbox('Canal', lista_canal)

        def df_filtro_canal():
            if filtro_canal == 'Todos':
                return df_vendas_filtrado
            else:
                return df_vendas_filtrado[df_vendas_filtrado['Canal de Vendas'] == filtro_canal]
        
        df_vendas_filtrado = df_filtro_canal()
        
        col2.metric(label='Venda Total', value=f'R$ {df_vendas_filtrado['Total da Venda (R$)'].sum():,.2f}')

    venda_por_canal = df_vendas_filtrado.groupby('Canal de Vendas')['Total da Venda (R$)'].sum().reset_index()
    venda_por_canal.sort_values(by='Total da Venda (R$)', ascending=False, inplace=True)
    venda_por_canal['part_%'] = venda_por_canal['Total da Venda (R$)'] / venda_por_canal['Total da Venda (R$)'].sum() * 100
    venda_por_canal['part_%'] = venda_por_canal['part_%'].round(2)

    fig_1 = px.bar(venda_por_canal, x='Total da Venda (R$)', y='Canal de Vendas',
                   title='Venda Por Canal (%)',
                   color='Canal de Vendas',
                   text='part_%',
                   width=750,
                   height=350)
    
    fig_1
    


if pagina == 'Compras':
    pagina_compras()
elif pagina == 'Vendas':
    pagina_vendas()