# %%

import pandas as pd
import numpy as np
from decimal import *
from calendar import monthrange
import datetime

produtos = pd.read_excel('base_brecho.xlsx', sheet_name='Produtos')
categorias = pd.read_excel('base_brecho.xlsx', sheet_name='Categorias')
clientes = pd.read_excel('base_brecho.xlsx', sheet_name='BaseClientes')
forma_pagamento = pd.read_excel('base_brecho.xlsx', sheet_name='FormaDePagamento')
estados = pd.read_csv('Municipios-Brasileiros/csv/estados.csv')
estados_regiao = pd.read_excel('base_brecho.xlsx', sheet_name='EstadoRegiao')

# Build clientes por estado, randomicamente
clientes['codigo_uf'] = clientes['id_cliente']. \
    map(lambda x: np.random.choice(estados['codigo_uf']))

# adding regiao e removendo a coluna RIGHT
estados = estados.merge(right=estados_regiao, how='left', left_on='nome', right_on='Estado')
estados = estados.drop(columns=['Estado'])


def get_rows_per_month(date):
    if date.month < 7:
        rand = np.random.randint(350, 405)
    else:
        rand = np.random.randint(410, 500)
    return rand


def build_month_year_date(year, month):
    return datetime.date(year, month, 1)


years_list = [2019, 2020]
months = pd.Series([build_month_year_date(x, y) for x in years_list for y in np.arange(1, 13)])
rows = pd.Series([get_rows_per_month(x) for x in months])
months = pd.Series([str(x.year) + '-' + str(x.month) + '-' + '1' for x in months])

df_rows_per_month_year = pd.DataFrame({'month_year': months, 'rows': rows.values})

requests_quantity = []
for i in range(len(months)):
    if i < 7:
        count_rows = np.random.randint(350, 405)
    else:
        count_rows = np.random.randint(410, 500)

    requests_quantity.append(count_rows)

month_size = pd.DataFrame({'month': months, 'requests_quantity': requests_quantity})
month_size['year'] = month_size['month'].map(lambda x: x[:4])

fato_pedidos = pd.DataFrame()
for month, requests_quantity in month_size.itertuples(index=False):
    # print(month + ' ' + requests_quantity)
    t = pd.DataFrame()
    t['id_pedido'] = np.arange(requests_quantity)

    # categoria randomization
    sub_category_id_list = categorias['id_categoria'].to_list()
    dec_low = Decimal(.2)
    dec_medium = Decimal(.2)
    dec_high = Decimal(.6)
    categoria_id_p = [dec_high, dec_medium, dec_low]
    t['id_categoria'] = t['id_pedido']. \
        map(lambda x: np.random.choice(sub_category_id_list, p=categoria_id_p))

    # produto randomization
    t['id_produto'] = t['id_categoria']. \
        map(lambda x: np.random.choice(produtos[produtos["id_categoria"] == x]["id_produto"]))

    # adicionando as parcelas
    t['id_forma_de_pagamento'] = t['id_categoria']. \
        map(lambda x: np.random.choice(forma_pagamento["id_forma_pagamento"], p=[Decimal(.15), Decimal(.3),
                                                                                 Decimal(.4), Decimal(.15)]))

    # baseado no tipo de pagamento, caso for crédito adicionar a quantidade de parcelas variavies no max 10
    t['quantidade_de_parcelas'] = t['id_forma_de_pagamento']. \
        map(lambda x:
            np.random.choice(np.arange(1, 11)) if x == 3 else 0
            )

    # adicionando quantidade de produtos
    t['quantidade_de_produtos'] = t['id_pedido']. \
        map(lambda x: np.random.choice(np.arange(1, 6), p=[
        Decimal(.3),
        Decimal(.3),
        Decimal(.2),
        Decimal(.15),
        Decimal(.05)
    ]))

    # adicionando coluna de mes
    t['mes_criacao'] = t['id_pedido'].map(lambda x: month)

    fato_pedidos = pd.concat([fato_pedidos, t])

# adicionando os clientes no final de tudo pq nois é vida louca
fato_pedidos['id_cliente'] = fato_pedidos.id_pedido.map(lambda x: np.random.choice(clientes[:600]['id_cliente']))
