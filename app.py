from flask import Flask
import sqlalchemy as sql
import pandas as pd
import dash  #(version 1.12.0)
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from copy import deepcopy
import plotly.graph_objects as go


from functions import calcular_stats_x_team, calcular_puntos, calcular_estadisticas_liga



# ----------------------------------------------------------------------
# Database connection
# connect_string = 'mysql+mysqlconnector://agmm23:mysqlpassword1a@agmm23.mysql.pythonanywhere-services.com/agmm23$xcouter_db'
connect_string = 'mysql+mysqlconnector://root:password@localhost/xcouter_2021'

sql_engine = sql.create_engine(connect_string)
query = "select * from playbyplay" #Todo Cambiar la query por una de alchemy



# ----------------------------------------------------------------------
# App Layout
#app = Flask(__name__)

app = dash.Dash(__name__, prevent_initial_callbacks=True)


#Preparar data Frames
#Dataframe de estadisticas
df = pd.read_sql_query(query, sql_engine)
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



app.layout = html.Div([
    html.H1('Equipo Local'),
    dcc.Dropdown(
        id='dropdown-team-local',
        options=[{'label': k, 'value': k} for k in sorted(teams_dict.values())],
        value=list(sorted(teams_dict.values()))[0]
    ),
    html.H1('Ataque'),
    html.H2('Shooting (FG)'),
    #TODO Grafico de barras que compara como se distribuyen sus puntos versus los puntos de la liga (de 2 y de 3)
    #TODO Grafico de barras que compara en sus tiros sus eficiencias versus las eficiencias de la liga (de 2 y de 3)
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
        dcc.Graph(id='graph-distr-LCI')
    ], style={'width': '48%', 'display': 'inline-block'}),
    # html.H2('Turnovers'),
    # html.H2('Rebounding'),
    # html.H2('Free Throws'),
    #
    #
    # html.H1('Defensa'),
    # html.H2('Shooting'),
    # html.H2('Turnovers'),
    # html.H2('Rebounding'),
    # html.H2('Free Throws'),

    #Grilla, inhabilito temporalmente
    # dash_table.DataTable(
    #     id='datatable-interactivity',
    #     columns=[
    #         {"name": i, "id": i, "deletable": True, "selectable": True, "hideable": True}
    #         #if i == "iso_alpha3" or i == "year" or i == "id"
    #         #else {"name": i, "id": i, "deletable": True, "selectable": True}
    #         for i in stats_df.columns
    #     ],
    #     data=stats_df.to_dict('records'),  # the contents of the table
    #     #editable=True,              # allow editing of data inside all cells
    #     filter_action="native",     # allow filtering of data by user ('native') or not ('none')
    #     sort_action="native",       # enables data to be sorted per-column by user or not ('none')
    #     sort_mode="multi",         # sort across 'multi' or 'single' columns
    #     column_selectable="multi",  # allow users to select 'multi' or 'single' columns
    #     row_selectable="multi",     # allow users to select 'multi' or 'single' rows
    #     row_deletable=True,         # choose if user can delete a row (True) or not (False)
    #     selected_columns=[],        # ids of columns that user selects
    #     selected_rows=[],           # indices of rows that user selects
    #     page_action="native",       # all data is passed to the table up-front or not ('none')
    #     page_current=0,             # page number that user is on
    #     page_size=15,                # number of rows visible per page
    #     style_cell={                # ensure adequate header width when text is shorter than cell's text
    #         'minWidth': 95, 'maxWidth': 95, 'width': 95
    #     },
    #     # style_cell_conditional=[    # align text columns to left. By default they are aligned to right
    #     #     {
    #     #         'if': {'column_id': c},
    #     #         'textAlign': 'left'
    #     #     } for c in ['country', 'iso_alpha3']
    #     # ],
    #     style_data={                # overflow cells' content into multiple lines
    #         'whiteSpace': 'normal',
    #         'height': 'auto'
    #     }
    # ),
    html.Br(),
    html.Br(),
    html.Div(id='bar-container')
])

#EQUIPO SELECCIONADO
@app.callback(
    [Output('graph-scatter-assists', 'figure'), Output('graph-parcat-assists', 'figure'), Output('graph-distr-LCI', 'figure')],
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
# GRAFICO DE BARRAS DE DISTRIBUCION DE LANZAMIENTO DE TIROS DE CAMPO
    index_team = stats_df_league_added[stats_df_league_added['TEAM'] == selected_team].index[0]
    index_promedio_liga = stats_df_league_added[stats_df_league_added['TEAM'] == 'PROMEDIO_LIGA'].index[0]

    colors2pts = ['gainsboro', ] * len(stats_df_league_added['TEAM'])
    colors3pts = ['grey', ] * len(stats_df_league_added['TEAM'])
    colors2pts[index_team] = 'coral'
    colors3pts[index_team] = 'cornflowerblue'
    colors2pts[index_promedio_liga] = 'coral'
    colors3pts[index_promedio_liga] = 'cornflowerblue'

    fig_distr_LCI = go.Figure(data=[
        go.Bar(name='3PTs', x=stats_df_league_added['TEAM'], y=stats_df_league_added['3PTA%'], marker_color=colors3pts),
        go.Bar(name='2Pts', x=stats_df_league_added['TEAM'], y=stats_df_league_added['2PTA%'], marker_color=colors2pts),

    ])

    fig_distr_LCI.update_layout(barmode='stack')

    return fig_asisst_vs_not_assisted, fig_parcat_assisted, fig_distr_LCI


#Callback para la tabla, inhabilito temporalmente
# @app.callback(
#     Output(component_id='bar-container', component_property='children'),
#     [Input(component_id='datatable-interactivity', component_property="derived_virtual_data"),
#      Input(component_id='datatable-interactivity', component_property='derived_virtual_selected_rows'),
#      Input(component_id='datatable-interactivity', component_property='derived_virtual_selected_row_ids'),
#      Input(component_id='datatable-interactivity', component_property='selected_rows'),
#      Input(component_id='datatable-interactivity', component_property='derived_virtual_indices'),
#      Input(component_id='datatable-interactivity', component_property='derived_virtual_row_ids'),
#      Input(component_id='datatable-interactivity', component_property='active_cell'),
#      Input(component_id='datatable-interactivity', component_property='selected_cells')]
# )
#
# def update_bar(all_rows_data, slctd_row_indices, slct_rows_names, slctd_rows,
#                order_of_rows_indices, order_of_rows_names, actv_cell, slctd_cell):
#     print('***************************************************************************')
#     print('Data across all pages pre or post filtering: {}'.format(all_rows_data))
#     print('---------------------------------------------')
#     print("Indices of selected rows if part of table after filtering:{}".format(slctd_row_indices))
#     print("Names of selected rows if part of table after filtering: {}".format(slct_rows_names))
#     print("Indices of selected rows regardless of filtering results: {}".format(slctd_rows))
#     print('---------------------------------------------')
#     print("Indices of all rows pre or post filtering: {}".format(order_of_rows_indices))
#     print("Names of all rows pre or post filtering: {}".format(order_of_rows_names))
#     print("---------------------------------------------")
#     print("Complete data of active cell: {}".format(actv_cell))
#     print("Complete data of all selected cells: {}".format(slctd_cell))
#
#     dff = pd.DataFrame(all_rows_data)
#
#     # used to highlight selected countries on bar chart
#     colors = ['#7FDBFF' if i in slctd_row_indices else '#0074D9'
#               for i in range(len(dff))]
#
#     if "TEAM" in dff:
#         return [
#             dcc.Graph(id='bar-chart',
#                       figure=px.bar(
#                           data_frame=dff,
#                           x="TEAM",
#                           y='AST',
#                           labels={"AST": "Asistencias"}
#                       ).update_layout(showlegend=False, xaxis={'categoryorder': 'total ascending'})
#                       .update_traces(marker_color=colors, hovertemplate="<b>%{y}%</b><extra></extra>")
#                       )
#         ]

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