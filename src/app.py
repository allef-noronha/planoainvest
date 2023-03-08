import dash
from dash import html, dcc, Input, Output, State, html, dash_table, ctx
import dash_bootstrap_components as dbc
import pandas as pd
from backend import *
import plotly.express as px
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
from numpy_financial import irr

file = OpenFile()
file.get_data(worksheet_name="Portosole 2")
sales = SalesTable(file.data)
cash_flow = CashFlow(sales)
cash_flow.Run()

app = dash.Dash(__name__, use_pages=False, external_stylesheets=[dbc.icons.FONT_AWESOME], suppress_callback_exceptions=True)
server = app.server

icons = [
    "fa fa-home me-2", 
    "fa fa-timeline me-2", 
    "fa fa-table me-2", 
    "fa fa-bar-chart me-2", 
    "fa fa-cog me-2",
    "fa-solid fa-sign-out me-2"
]

sidebar = html.Nav(
    [
        html.Div(
            [
                html.Ul(
                    [
                        html.Div(html.Span(html.I(className=icons[0])), id='button-0', className='icon'),
                        html.Div(html.Span(html.I(className=icons[1])), id='button-1', className='icon'),
                        html.Div(html.Span(html.I(className=icons[2])), id='button-2', className='icon'),
                        html.Div(html.Span(html.I(className=icons[3])), id='button-3', className='icon'),
                        html.Div(html.Span(html.I(className=icons[4])), id='button-4', className='icon'),
                        # html.Li(html.A(html.I(className="fa fa-home me-2", id='button-1',), href='#')),
                        # html.Li(html.A(html.I(className="fa fa-timeline me-2"), href='#')),
                        # html.Li(html.A(html.I(className="fa fa-table me-2"), href='#')),
                        # html.Li(html.A(html.I(className="fa fa-bar-chart me-2"), href='#')),
                        # html.Li(html.A(html.I(className="fa fa-cog me-2"), href='#')),
                    ],
                    id='set-01'
                ),
                html.Div(html.Span(html.I(className=icons[5])), className='icon', id='set-02'),
                # html.Div(html.I(className="fa-solid fa-sign-out me-2"), id='set-02'),
            ],
            id='sidebar-div'
        ),
    ],
    id='sidebar'
)

def currency(amount):
    currency = "R$ {:,.2f}".format(amount)
    main_currency, fractional_currency = currency.split('.')
    new_main_currency = main_currency.replace(',', '.')
    currency = new_main_currency + "," + fractional_currency
    currency
    return currency

def figure(value = 1, colors=['firebrick']*5, cost=False):
    

    import numpy as np
    vgv = [
        sales.table['Valor a Vista'][sales.table['Observação'] == 'Venda'].sum(),
        cash_flow.table['Entradas'].sum(),
    ]
    costs = [
        [
            sales.dt['Valor Obra'] * (sales.dt['INCC atual']/sales.dt['INCC base']), 
            sales.dt['Inv. Inicial'], 
            vgv[0]*sales.dt['Corretagem'],         
            vgv[0]*sales.dt['Impostos'], 
        ],
        [
            sales.dt['Valor Obra'] * (sales.dt['INCC atual']/sales.dt['INCC base']), 
            sales.dt['Inv. Inicial'], 
            vgv[0]*sales.dt['Corretagem'],
            cash_flow.table['Impostos'].sum(),            
        ]
    ]
    cash = [
        [vgv[0], sum(costs[0]), vgv[0] - sum(costs[0])],
        [vgv[1], sum(costs[1]), vgv[1] - sum(costs[1])],
        costs[0],
        costs[1],
    ]

    if cost:
        return [sum(costs[0]), sum(costs[1]), (1 - sum(costs[0])/vgv[0]), (1 - sum(costs[1])/vgv[1]), vgv]

    y = list(range(len(cash[value - 1])))

    fig = go.Figure(
        data = [
            go.Bar(
                y = y,
                x = cash[value - 1],
                name = 'À Vista',
                orientation = 'h',
                texttemplate='R$ %{x:,.2f}',
                marker_color=colors,
            ),
        ],
    )

    fig.update_layout(
        autosize=True,
        height=len(cash[value-1])*100/3,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0,
            pad=4
        ),
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        font_family= "Montserrat",
        font_size=15
    )

    #legend
    fig.update_layout(showlegend=False)

    #x axis
    fig.update_xaxes(visible=False)

    #y axis    
    fig.update_yaxes(visible=False)

    fig.update_yaxes(autorange="reversed")
    if value == 1 or value == 3:
        fig.update_xaxes(autorange="reversed")
    

    return fig

color = ['blue', 'firebrick', 'yellow']

# def card_0(number):
#     if number == 0:
#         return html.Div(
#             [
#                 html.H1("Dados", className='text-1'), 
#                 html.H1("Iniciais") 
#             ],
#             id="item" + str(number),
#             className="card"
#         )
#     elif number == 1:
#         return
#     elif number == 2:
#         return
#     elif number == 3:
#         return
#     elif number == 4:
#         return


def card_1(number):
    if number == 0:
        return html.Div(
            [
                html.H1("Cronograma", className='text-1'), 
                html.H1("Obra") 
            ],
            id="item" + str(number),
            className="card"
        )
    elif number == 1:
        return
    elif number == 2:
        return
    elif number == 3:
        return
    elif number == 4:
        return

fig_test = px.sunburst(sales.table, path=["Observação", "Periodo", "IDs Unidades"], values='Área',
                  color='Valor a Vista', hover_name="IDs Unidades", height=700, hover_data=["Entrada", "Obra", "Chaves", "Intercaladas", "Pós Obra"],
                #   color_continuous_scale='RdBu',
                  color_continuous_midpoint=np.average(sales.table['Valor a Vista'], weights=sales.table['Área']))
fig_test.update_layout(
    margin = dict(t=0, l=0, r=0, b=0),
    paper_bgcolor="rgba(0,0,0,0)", 
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="white",
)

fig_test_2 = px.treemap(sales.table, path=["Observação", "Periodo", "IDs Unidades"], values='Área',
                  color='Valor a Vista', hover_name="IDs Unidades", height=700, hover_data=["Entrada", "Obra", "Chaves", "Intercaladas", "Pós Obra"],
                #   color_continuous_scale='RdBu',
                  color_continuous_midpoint=np.average(sales.table['Valor a Vista'], weights=sales.table['Área']))
fig_test_2.update_layout(
    margin = dict(t=0, l=0, r=0, b=0),
    paper_bgcolor="rgba(0,0,0,0)", 
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="white",
)


df_aux = sales.table[sales.table['Observação'] == 'Venda'][:]
df_aux = df_aux[['IDs Unidades', 'Área', 'Valor/m²', 'Valor a Vista', 'Entrada', 'N. Entrada', 'Obra', 'N. Obra', 'Chaves', 'Intercaladas', 'N. Intercaladas', 'Frequencia Intercaladas', 'Pós Obra', 'N. Pós Obra', 'Data Venda']]
for i in [3, 4, 6, 8, 9, 12]:
    df_aux.iloc[:, i] = df_aux.iloc[:, i].apply(lambda x: "R$ {:,.2f}".format(x).replace(",", "X").replace(".", ",").replace("X", "."))
df_aux['Data Venda'] = df_aux['Data Venda'].dt.strftime("%b-%y")

fig0 = go.Figure(
    data = [
        go.Scatter(
            x = file.data[0]['Data Venda'],
            y = file.data[0]['Valor a Vista'],
            mode='markers',
            marker=dict(
                size=file.data[0]['Área'],
                sizemode='area',
                sizeref=2.*max(file.data[0]['Área'])/(40.**2),
                sizemin=4
            )
        ),
    ],
    layout = go.Layout(
        autosize=True,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=50,
            pad=4
        ),
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        # xaxis=dict(
        #     range = [-1, 45]
        # ),
        showlegend=False,
    )
)

def card_0(number):
    if number == 0:
        return html.Div(
            [
                html.H1("Dados", className='text-1'), 
                html.H1("Iniciais") 
            ],
            id="item" + str(number),
            className="card"
        )
    elif number == 1:
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(html.I(className="fas fa-piggy-bank me-2"), className='info-1'),
                        html.Div(
                            [
                                html.Div(html.H3("Área de Venda", style={'fontWeight':'200'}),className='info-2-1'),
                                html.Div(
                                    html.H2("{:.2f} m²".format(sales.table['Área'][sales.table['Observação']=="Venda"].sum()).replace(".", ",")),
                                    className='info-2-2'
                                ),
                                html.Div(
                                    [
                                        html.H5(
                                            "{:.1%}".format(sales.table['Área'][sales.table['Observação']=="Venda"].sum()/sales.table['Área'].sum()), 
                                            style={'color': 'rgb(59, 183, 255)'}
                                        ),
                                        html.H5("da Área Total"),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        )
                    ],
                    className='info'
                ),
            ],
            id="item" + str(number),
            className="card"
        )
    elif number == 2:
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(html.I(className="fas fa-piggy-bank me-2"), className='info-1'),
                        html.Div(
                            [
                                html.Div(html.H3("Área de Administração", style={'fontWeight':'200'}),className='info-2-1'),
                                html.Div(
                                    html.H2("{:.2f} m²".format(sales.table['Área'][sales.table['Observação']=="Administração"].sum()).replace(".", ",")),
                                    className='info-2-2'
                                ),
                                html.Div(
                                    [
                                        html.H5(
                                            "{:.1%}".format(sales.table['Área'][sales.table['Observação']=="Administração"].sum()/sales.table['Área'].sum()), 
                                            style={'color': 'rgb(59, 183, 255)'}
                                        ),
                                        html.H5("da Área Total"),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        )
                    ],
                    className='info'
                ),
            ],
            id="item" + str(number),
            className="card"
        )
    elif number == 3:
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(html.I(className="fas fa-piggy-bank me-2"), className='info-1'),
                        html.Div(
                            [
                                html.Div(html.H3("Área de Incorporação", style={'fontWeight':'200'}),className='info-2-1'),
                                html.Div(
                                    html.H2("{:.2f} m²".format(sales.table['Área'][sales.table['Observação']=="Incorporação"].sum()).replace(".", ",")),
                                    className='info-2-2'
                                ),
                                html.Div(
                                    [
                                        html.H5(
                                            "{:.1%}".format(sales.table['Área'][sales.table['Observação']=="Incorporação"].sum()/sales.table['Área'].sum()), 
                                            style={'color': 'rgb(59, 183, 255)'}
                                        ),
                                        html.H5("da Área Total"),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        )
                    ],
                    className='info'
                ),
            ],
            id="item" + str(number),
            className="card"
        )
    elif number == 4:
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(html.I(className="fas fa-piggy-bank me-2"), className='info-1'),
                        html.Div(
                            [
                                html.Div(html.H3("Início Operações", style={'fontWeight':'200'}),className='info-2-1'),
                                html.Div(html.H2(sales.t0.strftime("%b-%y")),className='info-2-2'),
                                html.Div(
                                    [
                                        html.H5("Mês"),
                                        html.H5("0", style={'color': 'rgb(59, 183, 255)'}),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        ),
                        html.Div(
                            [
                                html.Div(html.H3("Início Obra", style={'fontWeight':'200'}),className='info-2-1'),
                                html.Div(html.H2(cash_flow.table.iloc[sales.inicio_obra, 1].strftime("%b-%y")),className='info-2-2'),
                                html.Div(
                                    [
                                        html.H5("Mês"),
                                        html.H5(sales.inicio_obra, style={'color': 'rgb(59, 183, 255)'}),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        ),
                        html.Div(
                            [
                                html.Div(html.H3("Fim Obra", style={'fontWeight':'200'}),className='info-2-1'),
                                html.Div(html.H2(cash_flow.table.iloc[sales.fim_obra, 1].strftime("%b-%y")),className='info-2-2'),
                                html.Div(
                                    [
                                        html.H5("Mês"),
                                        html.H5(sales.fim_obra, style={'color': 'rgb(59, 183, 255)'}),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        ),
                        html.Div(
                            [
                                html.Div(html.H3("Fim Operações", style={'fontWeight':'200'}),className='info-2-1'),
                                html.Div(html.H2(cash_flow.table.iloc[len(cash_flow.table)-1, 1].strftime("%b-%y")),className='info-2-2'),
                                html.Div(
                                    [
                                        html.H5("Mês"),
                                        html.H5(len(cash_flow.table)-1, style={'color': 'rgb(59, 183, 255)'}),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        )
                    ],
                    className='info'
                ),
            ],
            id="item" + str(number),
            className="card"
        )
    elif number == 5:
        return html.Div(
            [
                html.Div(
                    [
                        dcc.Tabs(
                            [
                                dcc.Tab(
                                    [
                                        dash_table.DataTable(
                                            page_size=8,
                                            data=sales.business_conditions.to_dict('records'),
                                            columns=[{"name": i, "id": i} for i in sales.business_conditions.columns],
                                            filter_action="native",
                                            sort_action="native",
                                            style_table={"overflowX": "auto"},
                                            style_data={'color': 'black', 'background': 'white'},
                                            style_header={'font-weight': 'bold', 'color': 'black', 'background': 'rgb(210, 210, 210)'}
                                        )
                                    ],
                                    label='Tabela 1',
                                    style={'background': 'transparent', 'color': 'white', 'font-weight': '300', 'border': 'transparent', 'opacity': '0.8'},
                                    selected_style={'background': 'transparent', 'color': 'white', 'font-weight': '600', 'border': 'transparent'},
                                ),
                                dcc.Tab(
                                    [
                                        dash_table.DataTable(
                                            page_size=8,
                                            data=file.data[0].to_dict('records'),
                                            columns=[{"name": i, "id": i} for i in file.data[0].columns],
                                            filter_action="native",
                                            sort_action="native",
                                            style_table={"overflowX": "auto"},
                                            style_data={'color': 'black', 'background': 'white'},
                                            style_header={'font-weight': 'bold', 'color': 'black', 'background': 'rgb(210, 210, 210)'}
                                        )
                                    ],
                                    label='Tabela 2',
                                    style={'background': 'transparent', 'color': 'white', 'font-weight': '300', 'border': 'transparent', 'opacity': '0.8'},
                                    selected_style={'background': 'transparent', 'color': 'white', 'font-weight': '600', 'border': 'transparent'},
                                ),
                                # dcc.Tab(
                                #     [
            
                                #     ],
                                #     label='Tabela de Vendas',
                                #     style={'background': 'transparent', 'color': 'white', 'font-weight': '300', 'border': 'transparent', 'opacity': '0.8'},
                                #     selected_style={'background': 'transparent', 'color': 'white', 'font-weight': '600', 'border': 'transparent'},
                                # ),
                            ],
                            style={'background': 'transparent', 'width': '30%'}
                        ),
                    ],
                    style={'width': '100%', 'align-items': 'center', 'justify-content': 'start'}
                ),
            ],
            id="item" + str(number) + "-0",
            className="card"
        )
    elif number == 6:
        return html.Div(
            [
                dcc.Graph(
                    figure = fig0,
                    style={'width': '100%'}
                )
            ],
            id="item" + str(number) + "-0",
            className="card",
            style={'width': '100%'}
        )
    elif number == 7:
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(html.H3("Total de Unidades", style={'fontWeight':'200'}), style={'text-align': 'center'}),
                                html.Div(html.H2(sales.table['Periodo'].count()), style={'text-align': 'center'}),
                                html.Div(html.H3("Unidades à Venda", style={'fontWeight':'200'}), style={'text-align': 'center'}),
                                html.Div(html.H2(sales.table['Periodo'][sales.table['Observação'] == "Venda"].count()), style={'text-align': 'center'}),
                            ],
                            # className='info-1',
                            style={'justify-content': 'center', 'margin-left': '20px'}
                        ),
                        # html.Div(html.I(className="fas fa-piggy-bank me-2"), className='info-1'),
                        html.Div(
                            [
                                html.Div(html.H3("Antes da Obra", style={'fontWeight':'200'}), style={'text-align': 'center'}),
                                html.Div(html.H2(sales.table['Periodo'][sales.table['Observação'] == "Venda"].value_counts()['Antes da Obra']), style={'text-align': 'center'}),
                                html.Div(
                                    [
                                        html.H5("{:.1%}".format(sales.table['Periodo'][sales.table['Observação'] == "Venda"].value_counts()['Antes da Obra']/sales.table['Periodo'][sales.table['Observação'] == "Venda"].count()), style={'color': 'rgb(59, 183, 255)'}),
                                        html.H5("das Unidades"),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        ),
                        html.Div(
                            [
                                html.Div(html.H3("Durante a Obra", style={'fontWeight':'200'}), style={'text-align': 'center'}),
                                html.Div(html.H2(sales.table['Periodo'][sales.table['Observação'] == "Venda"].value_counts()['Durante a Obra']), style={'text-align': 'center'}),
                                html.Div(
                                    [
                                        html.H5("{:.1%}".format(sales.table['Periodo'][sales.table['Observação'] == "Venda"].value_counts()['Durante a Obra']/sales.table['Periodo'][sales.table['Observação'] == "Venda"].count()), style={'color': 'rgb(59, 183, 255)'}),
                                        html.H5("das Unidades"),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        ),
                        html.Div(
                            [
                                html.Div(html.H3("Pós Obra", style={'fontWeight':'200'}), style={'text-align': 'center'}),
                                html.Div(html.H2(sales.table['Periodo'][sales.table['Observação'] == "Venda"].value_counts()['Pós Obra']), style={'text-align': 'center'}),
                                html.Div(
                                    [
                                        html.H5("{:.1%}".format(sales.table['Periodo'][sales.table['Observação'] == "Venda"].value_counts()['Pós Obra']/sales.table['Periodo'][sales.table['Observação'] == "Venda"].count()), style={'color': 'rgb(59, 183, 255)'}),
                                        html.H5("das Unidades"),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        ),
                    ],
                    style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center', 'gap': '20px'}, 
                ),
            ],
            id="item" + str(number) + "-0",
            className="card"
        )
    elif number == 8:
        return html.Div(
            [
                html.Div(
                    [
                        html.H2("Tabela de Vendas", style={'margin': '15px'}),
                        dash_table.DataTable(
                            page_size=13,
                            data=df_aux.to_dict('records'),
                            columns=[{"name": i, "id": i} for i in df_aux.columns],
                            filter_action="native",
                            sort_action="native",
                            style_table={"overflowX": "auto"},
                            style_data={'color': 'black', 'background': 'white'},
                            style_header={'font-weight': 'bold', 'color': 'black', 'background': 'rgb(210, 210, 210)'}
                        )
                    ],
                    style={'width': '100%', 'align-items': 'center', 'justify-content': 'center'}
                ),
            ],
            id="item" + str(number) + "-2",
            className="card"
        )

def card_2(number):
    if number == 0:
        return html.Div(
            [
                html.H1("Tabela", className='text-1'), 
                html.H1("Vendas") 
            ],
            id="item" + str(number),
            className="card"
        )
    elif number == 1:
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(html.I(className="fa fa-building me-2"), className='info-1'),
                        html.Div(
                            [
                                html.Div(html.H3("Área de Venda", style={'fontWeight':'200'}),className='info-2-1'),
                                html.Div(
                                    html.H2("{:.2f} m²".format(sales.table['Área'][sales.table['Observação']=="Venda"].sum()).replace(".", ",")),
                                    className='info-2-2'
                                ),
                                html.Div(
                                    [
                                        html.H5(
                                            "{:.1%}".format(sales.table['Área'][sales.table['Observação']=="Venda"].sum()/sales.table['Área'].sum()), 
                                            style={'color': 'rgb(59, 183, 255)'}
                                        ),
                                        html.H5("da Área Total"),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        )
                    ],
                    className='info'
                ),
            ],
            id="item" + str(number),
            className="card"
        )
    elif number == 2:
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(html.I(className="fas fa-coins me-2"), className='info-1'),
                        html.Div(
                            [
                                html.Div(html.H3("Custo Base por m²", style={'fontWeight':'200'}),className='info-2-1'),
                                html.Div(html.H2(currency(sales.business_conditions['Valor'][5])),className='info-2-2'),
                                html.Div(
                                    [
                                        html.H5(
                                            "{:.2%}".format((sales.business_conditions['Valor'][5]/(sales.table['Valor a Vista'].sum()/sales.table['Área'].sum()))-1), 
                                            style={'color': 'rgb(59, 183, 255)'}
                                        ),
                                        html.H5("do Custo Médio"),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        )
                    ],
                    className='info'
                ),
            ],
            id="item" + str(number),
            className="card"
        )
    elif number == 3:
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(html.I(className="fas fa-clock me-2"), className='info-1'),
                        html.Div(
                            [
                                html.Div(html.H3("Duração da Obra", style={'fontWeight':'200'}),className='info-2-1'),
                                html.Div(html.H2("{} Meses".format(sales.dt['Obra']['Parcelas'])),className='info-2-2'),
                                html.Div(
                                    [
                                        html.H5("{:.1%}".format(sales.dt['Obra']['Parcelas']/len(cash_flow.table)), style={'color': 'rgb(59, 183, 255)'}),
                                        html.H5("do Tempo Total"),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        )
                    ],
                    className='info'
                ),
            ],
            id="item" + str(number),
            className="card"
        )
    elif number == 4:
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(html.I(className="fas fa-hard-hat me-2"), className='info-1'),
                        html.Div(
                            [
                                html.Div(html.H3("Início Operações", style={'fontWeight':'200'}),className='info-2-1'),
                                html.Div(html.H2(sales.t0.strftime("%b-%y")),className='info-2-2'),
                                html.Div(
                                    [
                                        html.H5("Mês"),
                                        html.H5("0", style={'color': 'rgb(59, 183, 255)'}),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        ),
                        html.Div(
                            [
                                html.Div(html.H3("Início Obra", style={'fontWeight':'200'}),className='info-2-1'),
                                html.Div(html.H2(cash_flow.table.iloc[sales.inicio_obra, 1].strftime("%b-%y")),className='info-2-2'),
                                html.Div(
                                    [
                                        html.H5("Mês"),
                                        html.H5(sales.inicio_obra, style={'color': 'rgb(59, 183, 255)'}),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        ),
                        html.Div(
                            [
                                html.Div(html.H3("Fim Obra", style={'fontWeight':'200'}),className='info-2-1'),
                                html.Div(html.H2(cash_flow.table.iloc[sales.fim_obra, 1].strftime("%b-%y")),className='info-2-2'),
                                html.Div(
                                    [
                                        html.H5("Mês"),
                                        html.H5(sales.fim_obra, style={'color': 'rgb(59, 183, 255)'}),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        ),
                        html.Div(
                            [
                                html.Div(html.H3("Fim Operações", style={'fontWeight':'200'}),className='info-2-1'),
                                html.Div(html.H2(cash_flow.table.iloc[len(cash_flow.table)-1, 1].strftime("%b-%y")),className='info-2-2'),
                                html.Div(
                                    [
                                        html.H5("Mês"),
                                        html.H5(len(cash_flow.table)-1, style={'color': 'rgb(59, 183, 255)'}),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        )
                    ],
                    className='info'
                ),
            ],
            id="item" + str(number),
            className="card"
        )
    elif number == 5:
        return html.Div(
            [
                html.Div(
                    [
                        dcc.Tabs(
                            [
                                dcc.Tab(
                                    [
                                        dcc.Graph(figure=fig_test),
                                    ],
                                    label='Gráfico 1',
                                    style={'background': 'transparent', 'color': 'white', 'font-weight': '300', 'border': 'transparent', 'opacity': '0.8'},
                                    selected_style={'background': 'transparent', 'color': 'white', 'font-weight': '600', 'border': 'transparent'},
                                ),
                                dcc.Tab(
                                    [
                                        dcc.Graph(figure=fig_test_2),
                                    ],
                                    label='Gráfico 2',
                                    style={'background': 'transparent', 'color': 'white', 'font-weight': '300', 'border': 'transparent', 'opacity': '0.8'},
                                    selected_style={'background': 'transparent', 'color': 'white', 'font-weight': '600', 'border': 'transparent'},
                                ),
                                # dcc.Tab(
                                #     [
            
                                #     ],
                                #     label='Tabela de Vendas',
                                #     style={'background': 'transparent', 'color': 'white', 'font-weight': '300', 'border': 'transparent', 'opacity': '0.8'},
                                #     selected_style={'background': 'transparent', 'color': 'white', 'font-weight': '600', 'border': 'transparent'},
                                # ),
                            ],
                            style={'background': 'transparent', 'width': '30%'}
                        ),
                    ],
                    style={'width': '100%', 'align-items': 'center', 'justify-content': 'start'}
                ),
            ],
            id="item" + str(number) + "-2",
            className="card"
        )
    elif number == 6:
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(html.H3("Total de Unidades", style={'fontWeight':'200'}), style={'text-align': 'center'}),
                                html.Div(html.H2(sales.table['Periodo'].count()), style={'text-align': 'center'}),
                                html.Div(html.H3("Unidades à Venda", style={'fontWeight':'200'}), style={'text-align': 'center'}),
                                html.Div(html.H2(sales.table['Periodo'][sales.table['Observação'] == "Venda"].count()), style={'text-align': 'center'}),
                            ],
                            # className='info-1',
                            style={'justify-content': 'center', 'margin-left': '20px'}
                        ),
                        # html.Div(html.I(className="fas fa-piggy-bank me-2"), className='info-1'),
                        html.Div(
                            [
                                html.Div(html.H3("Antes da Obra", style={'fontWeight':'200'}), style={'text-align': 'center'}),
                                html.Div(html.H2(sales.table['Periodo'][sales.table['Observação'] == "Venda"].value_counts()['Antes da Obra']), style={'text-align': 'center'}),
                                html.Div(
                                    [
                                        html.H5("{:.1%}".format(sales.table['Periodo'][sales.table['Observação'] == "Venda"].value_counts()['Antes da Obra']/sales.table['Periodo'][sales.table['Observação'] == "Venda"].count()), style={'color': 'rgb(59, 183, 255)'}),
                                        html.H5("das Unidades"),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        ),
                        html.Div(
                            [
                                html.Div(html.H3("Durante a Obra", style={'fontWeight':'200'}), style={'text-align': 'center'}),
                                html.Div(html.H2(sales.table['Periodo'][sales.table['Observação'] == "Venda"].value_counts()['Durante a Obra']), style={'text-align': 'center'}),
                                html.Div(
                                    [
                                        html.H5("{:.1%}".format(sales.table['Periodo'][sales.table['Observação'] == "Venda"].value_counts()['Durante a Obra']/sales.table['Periodo'][sales.table['Observação'] == "Venda"].count()), style={'color': 'rgb(59, 183, 255)'}),
                                        html.H5("das Unidades"),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        ),
                        html.Div(
                            [
                                html.Div(html.H3("Pós Obra", style={'fontWeight':'200'}), style={'text-align': 'center'}),
                                html.Div(html.H2(sales.table['Periodo'][sales.table['Observação'] == "Venda"].value_counts()['Pós Obra']), style={'text-align': 'center'}),
                                html.Div(
                                    [
                                        html.H5("{:.1%}".format(sales.table['Periodo'][sales.table['Observação'] == "Venda"].value_counts()['Pós Obra']/sales.table['Periodo'][sales.table['Observação'] == "Venda"].count()), style={'color': 'rgb(59, 183, 255)'}),
                                        html.H5("das Unidades"),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        ),
                    ],
                    style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center', 'gap': '20px'}, 
                ),
            ],
            id="item" + str(number) + "-2",
            className="card"
        )
    elif number == 7:
        return html.Div(
            [
                html.Div(
                    [
                        html.H2("Tabela de Vendas", style={'margin': '15px'}),
                        dash_table.DataTable(
                            page_size=13,
                            data=df_aux.to_dict('records'),
                            columns=[{"name": i, "id": i} for i in df_aux.columns],
                            filter_action="native",
                            sort_action="native",
                            style_table={"overflowX": "auto"},
                            style_data={'color': 'black', 'background': 'white'},
                            style_header={'font-weight': 'bold', 'color': 'black', 'background': 'rgb(210, 210, 210)'}
                        )
                    ],
                    style={'width': '100%', 'align-items': 'center', 'justify-content': 'center'}
                ),
            ],
            id="item" + str(number) + "-2",
            className="card"
        )

def card_3(number):
    if number == 0:
        return html.Div(
            [
                html.H1("Relatório", className='text-1'), 
                html.H1("Investidor") 
            ],
            id="item" + str(number),
            className="card"
        )
    elif number == 1:
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(html.I(className="fa fa-building me-2"), className='info-1'),
                        html.Div(
                            [
                                html.Div(html.H3("Área de Venda", style={'fontWeight':'200'}),className='info-2-1'),
                                html.Div(
                                    html.H2("{:.2f} m²".format(sales.table['Área'][sales.table['Observação']=="Venda"].sum()).replace(".", ",")),
                                    className='info-2-2'
                                ),
                                html.Div(
                                    [
                                        html.H5(
                                            "{:.1%}".format(sales.table['Área'][sales.table['Observação']=="Venda"].sum()/sales.table['Área'].sum()), 
                                            style={'color': 'rgb(59, 183, 255)'}
                                        ),
                                        html.H5("da Área Total"),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        )
                    ],
                    className='info'
                ),
            ],
            id="item" + str(number),
            className="card"
        )
    elif number == 2:
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(html.I(className="fas fa-coins me-2"), className='info-1'),
                        html.Div(
                            [
                                html.Div(html.H3("Custo Base por m²", style={'fontWeight':'200'}),className='info-2-1'),
                                html.Div(html.H2(currency(sales.business_conditions['Valor'][5])),className='info-2-2'),
                                html.Div(
                                    [
                                        html.H5(
                                            "{:.2%}".format((sales.business_conditions['Valor'][5]/(sales.table['Valor a Vista'].sum()/sales.table['Área'].sum()))-1), 
                                            style={'color': 'rgb(59, 183, 255)'}
                                        ),
                                        html.H5("do Custo Médio"),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        )
                    ],
                    className='info'
                ),
            ],
            id="item" + str(number),
            className="card"
        )
    elif number == 3:
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(html.I(className="fas fa-clock me-2"), className='info-1'),
                        html.Div(
                            [
                                html.Div(html.H3("Duração da Obra", style={'fontWeight':'200'}),className='info-2-1'),
                                html.Div(html.H2("{} Meses".format(sales.dt['Obra']['Parcelas'])),className='info-2-2'),
                                html.Div(
                                    [
                                        html.H5("{:.1%}".format(sales.dt['Obra']['Parcelas']/len(cash_flow.table)), style={'color': 'rgb(59, 183, 255)'}),
                                        html.H5("do Tempo Total"),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        )
                    ],
                    className='info'
                ),
            ],
            id="item" + str(number),
            className="card"
        )
    elif number == 4:
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(html.I(className="fas fa-hard-hat me-2"), className='info-1'),
                        html.Div(
                            [
                                html.Div(html.H3("Início Operações", style={'fontWeight':'200'}),className='info-2-1'),
                                html.Div(html.H2(sales.t0.strftime("%b-%y")),className='info-2-2'),
                                html.Div(
                                    [
                                        html.H5("Mês"),
                                        html.H5("0", style={'color': 'rgb(59, 183, 255)'}),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        ),
                        html.Div(
                            [
                                html.Div(html.H3("Início Obra", style={'fontWeight':'200'}),className='info-2-1'),
                                html.Div(html.H2(cash_flow.table.iloc[sales.inicio_obra, 1].strftime("%b-%y")),className='info-2-2'),
                                html.Div(
                                    [
                                        html.H5("Mês"),
                                        html.H5(sales.inicio_obra, style={'color': 'rgb(59, 183, 255)'}),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        ),
                        html.Div(
                            [
                                html.Div(html.H3("Fim Obra", style={'fontWeight':'200'}),className='info-2-1'),
                                html.Div(html.H2(cash_flow.table.iloc[sales.fim_obra, 1].strftime("%b-%y")),className='info-2-2'),
                                html.Div(
                                    [
                                        html.H5("Mês"),
                                        html.H5(sales.fim_obra, style={'color': 'rgb(59, 183, 255)'}),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        ),
                        html.Div(
                            [
                                html.Div(html.H3("Fim Operações", style={'fontWeight':'200'}),className='info-2-1'),
                                html.Div(html.H2(cash_flow.table.iloc[len(cash_flow.table)-1, 1].strftime("%b-%y")),className='info-2-2'),
                                html.Div(
                                    [
                                        html.H5("Mês"),
                                        html.H5(len(cash_flow.table)-1, style={'color': 'rgb(59, 183, 255)'}),
                                    ],
                                    className='info-2-3'
                                ),
                            ],
                            className='info-2'
                        )
                    ],
                    className='info'
                ),
            ],
            id="item" + str(number),
            className="card"
        )
    elif number == 5:
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H2("Resumo", className='text-1'),
                                        html.H2("Empreendimento"),
                                    ],
                                    className='title-1'
                                ),
                                # html.Hr(),
                                html.H2("Valores Gerais", className='text-1', style={'textAlign':'center', 'font-size':'1.2rem', 'margin-top': '20px', 'margin-bottom': '15px'}),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.H2("À Vista", id='title-item5'),
                                                html.Div(
                                                    [
                                                        dcc.Graph(figure=figure(1, color), config={'displayModeBar':False, }, className='text-1'),
                                                        html.H2("{:.1%}".format(figure(cost=True)[2]).replace(".", ",")),
                                                    ]
                                                )
                                            ],
                                            className='resume-1'
                                        ),

                                        html.Div(
                                            [
                                                html.H2("VS"),
                                                html.Div(
                                                    [
                                                        html.H2("VGV", style={'color': 'blue'}),
                                                        html.H2("Custo", style={'color': 'firebrick'}), 
                                                        html.H2("Resultado", style={'color': 'yellow'}),
                                                        html.H2("%"),
                                                    ]
                                                )
                                            ],
                                            className='resume-2'
                                        ),

                                        html.Div(
                                            [
                                                html.H2("Capitalizado"),
                                                html.Div(
                                                    [
                                                        dcc.Graph(figure=figure(2, color), config={'displayModeBar':False, }, className='text-1'),
                                                        html.H2("{:.1%}".format(figure(cost=True)[3]).replace(".", ",")),
                                                    ]
                                                )
                                            ],
                                            className='resume-3'
                                        ),
                                    ],
                                    className='resume'
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                html.H2("Detalhamento de Custos", className='text-1', style={'textAlign':'center', 'font-size':'1.2rem', 'margin-bottom': '15px'}),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                # html.H2("À Vista", id='title-item5'),
                                                html.Div(
                                                    [
                                                        dcc.Graph(figure=figure(3), config={'displayModeBar':False, }, className='text-1'),
                                                        html.H2(currency(figure(cost=True)[0])),
                                                    ]
                                                )
                                            ],
                                            className='resume-1'
                                        ),

                                        html.Div(
                                            [
                                                # html.H2("VS"),
                                                html.Div(
                                                    [
                                                        html.H2("Obra", style={'color': 'firebrick'}),
                                                        html.H2("Inv. Inicial", style={'color': 'firebrick'}), 
                                                        html.H2("Comissões", style={'color': 'firebrick'}),
                                                        html.H2("Impostos", style={'color': 'firebrick'}),
                                                        html.H2("Total"),
                                                    ]
                                                )
                                            ],
                                            className='resume-2'
                                        ),

                                        html.Div(
                                            [
                                                # html.H2("Capitalizado"),
                                                html.Div(
                                                    [
                                                        dcc.Graph(figure=figure(4), config={'displayModeBar':False, }, className='text-1'),
                                                        html.H2(currency(figure(cost=True)[1])),
                                                    ]
                                                )
                                            ],
                                            className='resume-3'
                                        ),
                                    ],
                                    className='resume'
                                ),
                                html.Hr(style={'margin-top': '15px'}),
                                
                            ]
                        ),
                        html.Div(
                            [
                                # html.Hr(),
                                html.H2("Indicadores Capitalizado", className='text-1', style={'textAlign':'center', 'font-size':'1.2rem'}),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.H3("Aporte Necessário", className='text-1'),
                                                html.H3("Taxa Interna de Retorno", className='text-1'),
                                                html.H3("Payback", className='text-1'),
                                                html.H3("ROI", className='text-1'),
                                            ]
                                        ),
                                        html.Div(
                                            [
                                                html.H3(currency(-cash_flow.table['Aportes Necessários'].sum())),
                                                html.H3("{:.2%} ao mês".format(irr(cash_flow.table['Fluxo'])).replace(".", ",")), 
                                                html.H3("{} Meses".format(cash_flow.table['Mês'][cash_flow.table['Fluxo Acumulado']<0].iloc[-1] + 1)),
                                                html.H3(
                                                    "À vista: {:.2%} | Capitalizado: {:.2%}".format(
                                                        figure(cost=True)[4][0]*figure(cost=True)[2]/-cash_flow.table['Aportes Necessários'].sum(),
                                                        figure(cost=True)[4][1]*figure(cost=True)[3]/-cash_flow.table['Aportes Necessários'].sum(),
                                                        ).replace(".", ",")),
                                                
                                            ],
                                            style={'textAlign': 'right'}
                                        ),
                                    ],
                                    id='indicadores-capitalizado'
                                ),

                            ]
                        ),
                    ],
                    id='main'
                ),
            ],
            id="item" + str(number),
            className="card"
        )
    elif number == 6:
        return html.Div(
            [
                html.Div(
                    [
                        html.H2("Resumo", className='text-1'),
                        html.H2("Investidor"),
                    ],
                    className='title-1'
                ),
                html.Div(
                    [
                        html.H2("Número de Cotas: "),
                        dcc.Input(
                            id="n-cotas", 
                            type="number",
                            value=1,
                            placeholder="Cotas",
                            min=1,
                            style={'color': 'white','width': '80px', 'background': 'black', 'fontWeight': '600', 'font-family': 'Montserrat', 'font-size': '1.2rem'}
                            ),
                    ],
                    style={'display': 'flex', 'gap': '10px'}
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H2("Aporte"),
                                html.H2(currency(cash_flow.input_value*cash_flow.investiment_output['Taxas'][0]))
                            ],
                            style={'display': 'flex', 'justify-content': 'space-between'}
                        ),
                        html.Div(id='table-input')    
                    ],
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H2("Remuneração"),
                                html.H2(currency(cash_flow.output_value))
                            ],
                            style={'display': 'flex', 'justify-content': 'space-between'}
                        ),
                        # table_output,
                        html.Div(id='table-output')                 
                    ],
                    style={'margin-bottom': '20px'}
                ),
            ],
            id="item" + str(number),
            className="card"
        )
    elif number == 7:
        return html.Div(
            [
                html.Div(
                    [
                        html.H2("TIR", className='text-1'),
                        html.H3(
                            "{:.2%} ao mês".format(irr(cash_flow.table['Remuneração']-cash_flow.table['Aporte'])).replace(".", ","),
                            style={'display': 'flex', 'font-size': '2rem', 'justify-content': 'center', 'margin-top': '15px'}
                        )
                    ]
                ),
                html.Div(
                    [
                        html.H2("ROI", className='text-1'),
                        html.H3(
                            "{:.2%}".format(cash_flow.output_value/cash_flow.input_value-1).replace(".", ","),
                            style={'display': 'flex', 'font-size': '2rem', 'justify-content': 'center', 'margin-top': '15px'},                            
                        )
                    ]
                ),
                html.Div(
                    [
                        html.H2("Meses Negativos", className='text-1'),
                        html.H3(
                            len(cash_flow.table[cash_flow.table['Fluxo com Investidor'].cumsum() < 0]),
                            style={'display': 'flex', 'font-size': '2rem', 'justify-content': 'center', 'margin-top': '15px'}, 
                        )
                    ]
                ),
            ],
            id="item" + str(number),
            className="card"
        )
    elif number == 8:
        return html.Div(
            [
                # html.H3("Card número {}".format(number)),
                dcc.Graph(id='graph-report'),
                html.Div(
                    [
                        dcc.Dropdown(
                            [
                                {
                                    "label": html.Span(['Análise de Aportes'], style={'color': 'royalblue', 'font-size': 17, 'font-weight': '600',}),
                                    "value": "fig1",
                                    "search": "Análise de Aportes"
                                },
                                {
                                    "label": html.Span(['Fluxo com Investidor'], style={'color': 'royalblue', 'font-size': 17, 'font-weight': '600',}),
                                    "value": "fig2",
                                    "search": "Fluxo de Caixa"
                                },
                                {
                                    "label": html.Span(['Fluxo de Caixa'], style={'color': 'royalblue', 'font-size': 17, 'font-weight': '600',}),
                                    "value": "fig3",
                                    "search": "Fluxo de Caixa"
                                },
                                {
                                    "label": html.Span(['Aporte e Remuneração'], style={'color': 'royalblue', 'font-size': 17, 'font-weight': '600',}),
                                    "value": "fig4",
                                    "search": "Aporte e Remuneração"
                                },
                                {
                                    "label": html.Span(['Cronograma de Obra'], style={'color': 'royalblue', 'font-size': 17, 'font-weight': '600',}),
                                    "value": "fig5",
                                    "search": "Cronograma de Obra"
                                },
                            ], 
                            value='fig1',
                            style={'width': '7cm','text-align': 'center', 'color': 'royalblue', 'background': 'transparent', 'font-family': 'Montserrat',},
                            id='dropdown-graph'
                        ),
                        html.H2(
                            "ao longo do tempo",
                            style={'color': 'white', 'font-size': 17, 'font-family': 'Montserrat', 'text-align': 'center', 'margin-top': '8px'}
                        )
                    ],
                    id='dropdown-graph-div'
                )
            ],
            id="item" + str(number),
            className="card"
        )

app.layout = html.Div(
    html.Div(
        [
            sidebar,
            html.Div(id='report')
        ],
        id='main-card',
    ),
    id='body'
)


# ========== Main ============
@app.callback(
    [Output('button-' + str(i), 'className') for i in range(len(icons)-1)]
    + [Output('report', 'children')],
    [Input('button-' + str(i), 'n_clicks') for i in range(len(icons)-1)],
)
def report(*btn):
    btn0, btn1, btn2, btn3, btn4 = ["icon"] * 5 
    if any(btn) == 0:
        report = html.Div(
            [
                card_0(i) for i in range(7)
            ],
            className='grid'
        )
        btn0 = "icon-2"
    if 'button-0' == ctx.triggered_id:
        btn0 = "icon-2"
        report = html.Div(
            [
                card_0(i) for i in range(7)
            ],
            className='grid'
        )
    elif 'button-1' == ctx.triggered_id:
        btn1 = "icon-2"
        report = html.Div(
            [
                card_1(i) for i in range(1)
            ],
            className='grid'
        )
    elif 'button-2' == ctx.triggered_id:
        btn2 = "icon-2"
        report = html.Div(
            [
                card_2(i) for i in range(8)
            ],
            className='grid'
        )
    elif 'button-3' == ctx.triggered_id:
        btn3 = "icon-2"
        report = html.Div(
            [
                card_3(i) for i in range(9)
            ],
            className='grid'
        )
    elif 'button-4' == ctx.triggered_id:
        btn4 = "icon-2"
        report = html.Div(
            [
                html.H1("Configurações")
            ]
        )
    return btn0, btn1, btn2, btn3, btn4, report

# ========== Home ============

# ========== Cronograma ============

# ========== Tabela de Vendas ============

# ========== Relatório ============

@app.callback(
    [Output('graph-report', 'figure')][0],
    [
        Input('dropdown-graph', 'value'),
        Input('button-3', 'n_clicks')
    ],
)
def update_graphs(value, btn):
    if btn == 0:
        raise PreventUpdate
    if value == 'fig1':
        return fig1
    elif value == 'fig2':
        return fig2
    elif value == 'fig3':
        return fig3
    elif value == 'fig4':
        return fig4
    else:
        return fig5
    
@app.callback(
    [
        Output('table-input', 'children'),
        Output('table-output', 'children'),
    ],
    [Input('n-cotas', 'value')],
)
def update_tables(cota):
    def table_div(value):
        if value == 'in':
            data = cash_flow.investiment_input[:]
        else:
            data = cash_flow.investiment_output[:]
        table_data = data[:]
        table_data = table_data[table_data['Parcelas'] > 0]
        table_data['Valor Cota'] = table_data['Valor'] / cota
        table_data['Total'] = table_data['Valor Cota'] * table_data['Parcelas']

        table_data['Data Inicial'] = table_data['Data Inicial'].dt.strftime("%b-%y")
        table_data["Valor"] = table_data["Valor"].apply(lambda x: "R$ {:,.2f}".format(x))
        table_data["Valor Cota"] = table_data["Valor Cota"].apply(lambda x: "R$ {:,.2f}".format(x))
        table_data.loc[len(table_data.index)] = [""] * 7 + [table_data['Total'].sum()]
        table_data["Total"] = table_data["Total"].apply(lambda x: "R$ {:,.2f}".format(x))
        df = table_data.iloc[:,[0, 2, 3, 6, 7]]
        df.rename(columns = {'Periodicidade':'Freq.'}, inplace = True)
        table = dash_table.DataTable(
            page_size=3,
            data=df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in df.columns],
            style_as_list_view=True,
            # filter_action="native",
            # sort_action="native",
            style_table={"overflowX": "auto"},
            style_data={'color': 'white', 'background': 'transparent', 'text-align': 'center'},
            style_header={'font-weight': 'bold', 'color': 'black', 'background': 'rgb(210, 210, 210)', 'text-align': 'center'}
        )
        # return table_data
        # table = html.Div(
        #     [
        #         html.Div(
        #             [
        #                 html.Div(
        #                     [
        #                         table_data.columns.tolist()[i]
        #                     ],
        #                     className='header-item'
        #                 )
        #                 for i in [0, 2, 3, 6, 5]
        #             ],
        #             className='table-header'
        #         ),
        #         html.Div(
        #             [
        #                 html.Div(
        #                     [
        #                         html.Div(
        #                             [
        #                                 table_data.iloc[j].tolist()[i]
        #                             ],
        #                             className='table-data'
        #                         )
        #                         for i in [0, 2, 3, 6, 5]
        #                     ],
        #                     className='table-row'
        #                 )
        #                 for j in range(len(table_data))
        #             ],
        #             className='table-content'
        #         ),
        #     ],
        #     className='table'
        # )
        return table
    return table_div('in'), table_div('out')

aux = cash_flow.table['Aportes Necessários'].cumsum() - cash_flow.table['Aportes Necessários'].cumsum()[len(cash_flow.table)-1]
n = aux[aux > 0].count()

fig1 = go.Figure(
    data = [
        go.Bar(
            x = cash_flow.table['Data'],
            y = cash_flow.table['Aporte'],
            yaxis='y1',
            marker_color = 'blue',
            name="Aporte Investidor"
        ),
        go.Bar(
            x = cash_flow.table['Data'],
            y = -cash_flow.table['Aportes Necessários'],
            yaxis='y1',
            marker_color = 'white',
            name="Aporte Necessário"
        ),
        go.Scatter(
            x = cash_flow.table['Data'],
            y = cash_flow.table['Aporte'].cumsum(),
            yaxis='y2',
            line=dict(color='blue', width=4, dash='dash'),
            name="Aporte Inv. Acum."
        ),
        go.Scatter(
            x = cash_flow.table['Data'],
            y = -cash_flow.table['Aportes Necessários'].cumsum(),
            yaxis='y2',
            line = dict(color='white', width=4, dash='dash'),
            name="Aporte Nec. Acum"
        ),
    ],
    layout = go.Layout(
        autosize=True,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=50,
            pad=4
        ),
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        yaxis2 = dict(
            title="acumulado",
            titlefont=dict(
                color="blue"
            ),
            tickfont=dict(
                color="blue"
            ),
            anchor="x",
            overlaying="y",
            side="right",
            gridcolor = "blue"
        ),
        xaxis=dict(
            range = [cash_flow.table['Data'][0] - pd.DateOffset(months=1), cash_flow.table['Data'][n + 2]]
        ),
        # legend=dict(
        #     orientation="h",
        #     yanchor="bottom",
        #     y=1.02,
        #     xanchor="right",
        #     x=1,
        #     entrywidth=70,
        # ),
    )
)

fig2 = go.Figure(
    data = [
        go.Bar(
            x = cash_flow.table['Data'],
            y = cash_flow.table['Fluxo com Investidor'],
            yaxis='y1',
            marker_color = 'royalblue'
        ),
        go.Scatter(
            x = cash_flow.table['Data'],
            y = cash_flow.table['Fluxo com Investidor'].cumsum(),
            yaxis='y2',
            line=dict(color='blue', width=4, dash='dash')
        ),
    ],
    layout = go.Layout(
        autosize=True,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=50,
            pad=4
        ),
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        yaxis2 = dict(
            title="acumulado",
            titlefont=dict(
                color="#d62728"
            ),
            tickfont=dict(
                color="#d62728"
            ),
            anchor="x",
            overlaying="y",
            side="right"
        ),
        # xaxis=dict(
        #     range = [-1, 45]
        # ),
        showlegend=False,
    )
)

fig3 = go.Figure(
    data = [
        go.Bar(
            x = cash_flow.table['Data'],
            y = cash_flow.table['Fluxo'],
            texttemplate='%{y:.2s}',
            marker_color = 'blue'
        ),
        # go.Scatter(
        #     x = cash_flow.table['Data'],
        #     y = cash_flow.table['Fluxo'].cumsum(),
        #     yaxis='y2',
        #     line=dict(color='blue', width=4, dash='dash')
        # ),
    ],
    layout = go.Layout(
        autosize=True,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=50,
            pad=4
        ),
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        showlegend=False,
    )
)

fig4 = go.Figure(
    data = [
        go.Bar(
            x = cash_flow.table['Data'],
            y = -cash_flow.table['Aporte'],
            texttemplate='%{y:.2s}',
            marker_color = 'red'
        ),
        go.Bar(
            x = cash_flow.table['Data'],
            y = cash_flow.table['Remuneração'],
            texttemplate='%{y:.2s}',
            marker_color = 'blue'
        ),
    ],
    layout = go.Layout(
        autosize=True,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=50,
            pad=4
        ),
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        showlegend=False,
    )
)

fig5 = go.Figure(
    data = [
        go.Bar(
            x = sales.construction_schedule['Data'],
            y = sales.construction_schedule['R$'],
            texttemplate='%{y:.2s}',
            marker_color = 'blue'
        ),
        # go.Bar(
        #     x = cash_flow.table['Mês'],
        #     y = cash_flow.table['Remuneração']
        # ),
    ],
    layout = go.Layout(
        autosize=True,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=50,
            pad=4
        ),
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
    )
)

if __name__ == "__main__":
    app.run(debug=True, port="8054")