from flask import Flask
import sqlalchemy as sql
import pandas as pd
import dash  #(version 1.12.0)
from dash.dependencies import Input, Output, State
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from copy import deepcopy
import plotly.graph_objects as go
import dash_bootstrap_components as dbc


from functions import calcular_stats_x_team, calcular_puntos, calcular_estadisticas_liga, \
    Grafico_barras_acumulado_2, Grafico_barras_simple, player_stats_df, agregar_team_a_statsxplayer, \
    Grafico_barras_simple_players, x_team_stats_df
from components.navbar import Navbar



# ----------------------------------------------------------------------
# Database connection
# connect_string = 'mysql+mysqlconnector://agmm23:mysqlpassword1a@agmm23.mysql.pythonanywhere-services.com/agmm23$xcouter_db'
connect_string = 'mysql+mysqlconnector://root:password@localhost/xcouter_2021'

sql_engine = sql.create_engine(connect_string)
query = "select * from playbyplay" #Todo Cambiar la query por una de alchemy



# ----------------------------------------------------------------------
# App Layout
#app = Flask(__name__)

app = dash.Dash(__name__, prevent_initial_callbacks=True, external_stylesheets=[dbc.themes.BOOTSTRAP])


#Preparar data Frames
#Dataframe de estadisticas
df = pd.read_sql_query(query, sql_engine)

#Dataframe por player

player_stats_df = player_stats_df(df)

player_stats_df_with_team = agregar_team_a_statsxplayer(player_stats_df, df)

stats_df = calcular_stats_x_team(df)
stats_df.reset_index(inplace=True)

stats_df_league_added = stats_df.append(calcular_estadisticas_liga(stats_df))
stats_df_league_added.reset_index(inplace=True)
stats_df_league_added.drop('index', axis=1, inplace=True)

#Agrego

keep = (df['team_name'] != "")
df= df[keep].dropna(how='all')

#Lista para combo
teams = df['team_name'].unique()
teams_dict = dict(enumerate(teams.flatten(), 1))

pointsperplayer = pd.DataFrame()

#Preparacion de datos para el scatter plot de asistencias
df_assists = deepcopy(df)
df_assists['points'] = df_assists.apply(lambda x:calcular_puntos(x), axis=1)

playbyplay_points = df_assists[df_assists['points']>0]
pointsperplayer = pd.DataFrame()
pointsperplayer['assisted'] = playbyplay_points[playbyplay_points['Complementary_player'].notnull()].groupby(['player_x','team_name'])['points'].sum()
# pointsperplayer['not_assisted'] = playbyplay_points[playbyplay_points['Complementary_player']=='0'].groupby(['player_x','team_name'])['points'].sum()
pointsperplayer['not_assisted'] = playbyplay_points[playbyplay_points['Complementary_player'].isnull()].groupby(['player_x','team_name'])['points'].sum()
pointsperplayer.reset_index(inplace=True)
pointsperplayer.fillna(0, inplace=True)




navbar = Navbar()

app.layout = html.Div([
    navbar,
    html.Br(),
    dcc.Dropdown(
        id='dropdown-team-local',
        options=[{'label': k, 'value': k} for k in sorted(teams_dict.values())],
        value=list(sorted(teams_dict.values()))[0]
    ),
    html.H1('Ataque'),
    dbc.Row([
        dbc.Col([
            dbc.CardHeader(
                dbc.Button(
                    "Shooting (FG)",
                    color="link",
                    id="btn-shooting-attack",
                )
            ),
                #TODO Grafico de barras que compara como se distribuyen sus puntos versus los puntos de la liga (de 2 y de 3)
                #TODO Grafico de barras que compara en sus tiros sus eficiencias versus las eficiencias de la liga (de 2 y de 3)

            dbc.Collapse(
                dbc.CardBody(children=[
                    html.Div([
                        html.H3('Puntos anotados - Con asistencia vs sin asistencia'),
                        dcc.Graph(id='graph-scatter-assists')
                    ], style={'width': '48%', 'display': 'inline-block'}),
                    html.Div([
                        html.H3('Relación asistidor anotador'),
                        dcc.Graph(id='graph-parcat-assists')
                    ], style={'width': '48%', 'display': 'inline-block'}),
                    html.Div([
                        html.H3('Distribución de Lanzamientos de campo'),
                        dcc.Graph(id='graph-distr-LCI-attack')
                    ], style={'width': '48%', 'display': 'inline-block'}),
                ]),
                id="collapse-shooting-attack", is_open=False
            ),
        ], width=12),
    ]),
    #TURNOVERS EN ATAQUE ******************************************
    dbc.Row([
        dbc.Col([
            dbc.CardHeader(
                dbc.Button(
                    "Turnovers (TO)",
                    color="link",
                    id="btn-turnovers-attack",
                )
            ),
        ], width=12),
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Collapse(
                dbc.CardBody(
                    children=[
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    dcc.Graph(id='graph-TO-team-attack')
                                ],)
                            ], width=6),
                            dbc.Col([
                                html.Div([
                                    dcc.Graph(id='graph-TO-player-attack')
                                ])
                            ], width=6),
                        ])
                    ]
                ),
            id="collapse-turnovers-attack", is_open=False)
        ], width = 12)
    ]),

    #REBOTES EN ATAQUE ******************************************

    dbc.Row([
        dbc.Col([
            dbc.CardHeader(
                dbc.Button(
                    "Rebounding",
                    color="link",
                    id="btn-rebounding-attack",
                )
            ),
        ], width=12),
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Collapse(
                dbc.CardBody(
                    children=[
                        html.Div([
                            dcc.Graph(id='graph-OffRebounds-team_attack')
                        ])
                    ]
                ),
                id="collapse-rebounding-attack", is_open=False)
        ], width=6)
    ]),


    # Tiros Libres ******************************************

        dbc.Row([
            dbc.Col([
                dbc.CardHeader(
                    dbc.Button(
                        "Free Throws",
                        color="link",
                        id="btn-free_throws-attack",
                    )
                ),
            ], width=12),
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Collapse(
                    dbc.CardBody(
                        children=[
                            html.Div([
                                html.H3('Agregar aca graficos de Tiros libres'),
                            ])
                        ]
                    ),
                    id="collapse-free_throws-attack", is_open=False)
            ], width=6)
        ]),

    #TODO Considerar las faltas personales recibidas ya que sería lo que importa en ataque
#DEFENSA--------------------------------------------------------------------------------------
    #TIROS---------------------------------------
    dbc.Row([
        dbc.Col([
            dbc.CardHeader(
                dbc.Button(
                    "Shooting (FG)",
                    color="link",
                    id="btn-shooting-defense",
                )
            ),
            # TODO Grafico de barras que compara como se distribuyen sus puntos versus los puntos de la liga (de 2 y de 3)
            # TODO Grafico de barras que compara en sus tiros sus eficiencias versus las eficiencias de la liga (de 2 y de 3)
            dbc.Collapse(
                dbc.CardBody(children=[
                    html.Div([
                        html.H3('Distribución de Lanzamientos de campo'),
                        dcc.Graph(id='graph-distr-LCI-defense')
                    ], style={'width': '48%', 'display': 'inline-block'}),
                ]),
                id="collapse-shooting-defense", is_open=False
            ),
        ], width=12),

    ]),
    dbc.Row([

    ]),
    dbc.Row([

    ]),
    dbc.Row([

    ]),


    #========================================================================
    #LAYOUT
    html.Br(),
    html.Br(),
    html.H1('Defensa'),
    html.H2('Shooting'),
    html.H2('Turnovers'),
    html.H2('Rebounding'),
    dbc.CardHeader(
        dbc.Button(
            "Free Throws",
            color="link",
            id="btn-free-throws-defensive",
        )
    ),
    dbc.Collapse(
        dbc.CardBody("Graficos de free throws"),
        id="collapse-free-throws-defensive", is_open=False
    ),
    # Grilla, inhabilito temporalmente
    dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i, "deletable": True, "selectable": True, "hideable": True}
            #if i == "iso_alpha3" or i == "year" or i == "id"
            #else {"name": i, "id": i, "deletable": True, "selectable": True}
            for i in stats_df.columns
        ],
        data=stats_df.to_dict('records'),  # the contents of the table
        #editable=True,              # allow editing of data inside all cells
        filter_action="native",     # allow filtering of data by user ('native') or not ('none')
        sort_action="native",       # enables data to be sorted per-column by user or not ('none')
        sort_mode="multi",         # sort across 'multi' or 'single' columns
        column_selectable="multi",  # allow users to select 'multi' or 'single' columns
        row_selectable="multi",     # allow users to select 'multi' or 'single' rows
        row_deletable=True,         # choose if user can delete a row (True) or not (False)
        selected_columns=[],        # ids of columns that user selects
        selected_rows=[],           # indices of rows that user selects
        page_action="native",       # all data is passed to the table up-front or not ('none')
        page_current=0,             # page number that user is on
        page_size=15,                # number of rows visible per page
        style_cell={                # ensure adequate header width when text is shorter than cell's text
            'minWidth': 95, 'maxWidth': 95, 'width': 95
        },
        # style_cell_conditional=[    # align text columns to left. By default they are aligned to right
        #     {
        #         'if': {'column_id': c},
        #         'textAlign': 'left'
        #     } for c in ['country', 'iso_alpha3']
        # ],
        style_data={                # overflow cells' content into multiple lines
            'whiteSpace': 'normal',
            'height': 'auto'
        }
    ),
    html.Br(),
    html.Br(),
    html.Div(id='bar-container')
])

#Callbacks de los collapse elements
#----------------------------------------------------------------------------------------------------------------------
# ATAQUE
#Shooting
@app.callback(
    Output("collapse-shooting-attack", "is_open"),
    [Input("btn-shooting-attack", "n_clicks")],
    [State("collapse-shooting-attack", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
#Turnovers
@app.callback(
    Output("collapse-turnovers-attack", "is_open"),
    [Input("btn-turnovers-attack", "n_clicks")],
    [State("collapse-turnovers-attack", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
#Rebounding
@app.callback(
    Output("collapse-rebounding-attack", "is_open"),
    [Input("btn-rebounding-attack", "n_clicks")],
    [State("collapse-rebounding-attack", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
#Free throws
@app.callback(
    Output("collapse-free_throws-attack", "is_open"),
    [Input("btn-free_throws-attack", "n_clicks")],
    [State("collapse-free_throws-attack", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

#DEFENSA
#Shooting
@app.callback(
    Output("collapse-shooting-defense", "is_open"),
    [Input("btn-shooting-defense", "n_clicks")],
    [State("collapse-shooting-defense", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open



@app.callback(
    Output("collapse-free-throws-defensive", "is_open"),
    [Input("btn-free-throws-defensive", "n_clicks")],
    [State("collapse-free-throws-defensive", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open



#EQUIPO SELECCIONADO
@app.callback(
    [Output('graph-scatter-assists', 'figure'), Output('graph-parcat-assists', 'figure'), Output('graph-distr-LCI-attack', 'figure'),
     Output('graph-distr-LCI-defense', 'figure'), Output('graph-TO-team-attack', 'figure'),
     Output('graph-OffRebounds-team_attack', 'figure'), Output('graph-TO-player-attack', 'figure')],
    [Input('dropdown-team-local', 'value')])

def update_figures(selected_team):
#-----------------------------------------------------------------------------------------------------------------------
# SCATTER PLOT DE ASISTENCIAS
    pointsperplayer_team = pointsperplayer[pointsperplayer['team_name']==selected_team]

    fig_asisst_vs_not_assisted = go.Figure(data=go.Scatter(
        x=pointsperplayer_team['assisted'],
        y=pointsperplayer_team['not_assisted'],
        mode='markers',
        hovertemplate=
        '<b>%{text}</b>' +
        '<br><i>assisted</i>: %{x}' +
        '<br><i>not_assisted</i>: %{y}',
        text=pointsperplayer_team['player_x'],
        marker=dict(
            size=10,  # set color equal to a variable
            colorscale='YlGnBu',  # one of plotly colorscales
            showscale=False
        )
    ))

    fig_asisst_vs_not_assisted.update_xaxes(showspikes=True)
    fig_asisst_vs_not_assisted.update_yaxes(showspikes=True)

    fig_asisst_vs_not_assisted.update_layout(
        title="Plot Title",
        xaxis_title="Points Assisted",
        yaxis_title="Points NOT Assisted")
#-----------------------------------------------------------------------------------------------------------------------
# PARCAT PLOT DE ASISTENCIAS

    playbyplay_assisted = playbyplay_points[
        (playbyplay_points['Complementary_player'].notnull()) & (playbyplay_points['team_name'] == selected_team)]
    pbp_parcat_assisted = playbyplay_assisted.groupby(['player_x', 'Complementary_player'])['points'].sum()
    pbp_parcat_assisted = pd.DataFrame(pbp_parcat_assisted)
    pbp_parcat_assisted.reset_index(inplace=True)
    pbp_parcat_assisted.sort_values('points', ascending=False)

    fig_parcat_assisted = go.Figure(go.Parcats(
        dimensions=[
            {'label': 'Asistidor',
             'values': pbp_parcat_assisted['Complementary_player']},
            {'label': 'Anotador',
             'values': pbp_parcat_assisted['player_x']}],
        counts=pbp_parcat_assisted['points'],
        line={'color': pbp_parcat_assisted['points'], 'colorscale': 'YlGnBu'}
    ))

#-----------------------------------------------------------------------------------------------------------------------
#ATAQUE
# GRAFICO DE BARRAS DE DISTRIBUCION DE LANZAMIENTO DE TIROS DE CAMPO EN ATAQUE

    fig_distr_LCI_attack = Grafico_barras_acumulado_2(stats_df_league_added, selected_team, '2PTA%', '3PTA%', '2Pts', '3PTs')

# GRAFICO DE BARRAS DE DISTRIBUCION DE TURNOVERS EN ATAQUE
    #Por equipo
    fig_TO_team_attack = Grafico_barras_simple(stats_df_league_added, selected_team, 'TOV%', 'Turnovers')
    #Por jugador
    player_stats_df_with_team_to_graph = x_team_stats_df(player_stats_df_with_team, selected_team)
    fig_TO_player_attack = Grafico_barras_simple_players(player_stats_df_with_team_to_graph, 'TOR%', 'Turnovers')


# GRAFICO DE BARRAS DE DISTRIBUCION DE TURNOVERS EN ATAQUE
    fig_Off_Reb_attack = Grafico_barras_simple(stats_df_league_added, selected_team, 'OREB%', 'Offensive Rebound')


#-----------------------------------------------------------------------------------------------------------------------
#DEFENSA
# GRAFICO DE BARRAS DE DISTRIBUCION DE LANZAMIENTO DE TIROS DE CAMPO EN DEFENSA

    fig_distr_LCI_defense = Grafico_barras_acumulado_2(stats_df_league_added, selected_team, '2PTA%', '3PTA%', '2Pts', '3PTs')



    return fig_asisst_vs_not_assisted, fig_parcat_assisted, fig_distr_LCI_attack, fig_distr_LCI_defense, \
           fig_TO_team_attack, fig_Off_Reb_attack, fig_TO_player_attack


# Callback para la tabla, inhabilito temporalmente
@app.callback(
    Output(component_id='bar-container', component_property='children'),
    [Input(component_id='datatable-interactivity', component_property="derived_virtual_data"),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_selected_rows'),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_selected_row_ids'),
     Input(component_id='datatable-interactivity', component_property='selected_rows'),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_indices'),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_row_ids'),
     Input(component_id='datatable-interactivity', component_property='active_cell'),
     Input(component_id='datatable-interactivity', component_property='selected_cells')]
)

def update_bar(all_rows_data, slctd_row_indices, slct_rows_names, slctd_rows,
               order_of_rows_indices, order_of_rows_names, actv_cell, slctd_cell):
    print('***************************************************************************')
    print('Data across all pages pre or post filtering: {}'.format(all_rows_data))
    print('---------------------------------------------')
    print("Indices of selected rows if part of table after filtering:{}".format(slctd_row_indices))
    print("Names of selected rows if part of table after filtering: {}".format(slct_rows_names))
    print("Indices of selected rows regardless of filtering results: {}".format(slctd_rows))
    print('---------------------------------------------')
    print("Indices of all rows pre or post filtering: {}".format(order_of_rows_indices))
    print("Names of all rows pre or post filtering: {}".format(order_of_rows_names))
    print("---------------------------------------------")
    print("Complete data of active cell: {}".format(actv_cell))
    print("Complete data of all selected cells: {}".format(slctd_cell))

    dff = pd.DataFrame(all_rows_data)

    # used to highlight selected countries on bar chart
    colors = ['#7FDBFF' if i in slctd_row_indices else '#0074D9'
              for i in range(len(dff))]

    if "TEAM" in dff:
        return [
            dcc.Graph(id='bar-chart',
                      figure=px.bar(
                          data_frame=dff,
                          x="TEAM",
                          y='AST',
                          labels={"AST": "Asistencias"}
                      ).update_layout(showlegend=False, xaxis={'categoryorder': 'total ascending'})
                      .update_traces(marker_color=colors, hovertemplate="<b>%{y}%</b><extra></extra>")
                      )
        ]

#
# @app.route('/')
# def index():
#     return df['id_match'][0]

# FLASK
# if __name__ == '__main__':
#     app.run(debug=True)

# DASH
if __name__ == '__main__':
    app.run_server(debug=True)