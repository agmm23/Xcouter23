from flask import Flask
import sqlalchemy as sql
import pandas as pd
import dash  #(version 1.12.0)
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px


def calcular_stats_x_team(df):
    '''stats_df: This function returns the Assists (AST), Steals (STL), Blocks (BLK), Offensive Rebounds (ORB), Defensive Rebounds (DRB), Opponent ORB (OppORB), Opponent DRB (OppDRB), Turnovers (TO), Opponent Turnovers (OppTO),
Free Throw Attempts (FTA), Free Throws Made (FT), 2 Point Shot Attempts (2PTA), 2 Point Shots Made (2PT), 3 Point Shot Attempts (3PTA), 3 Point Shots Made (3PT),
Field Goal Attempted (FGA), Field Goals Made (FG), Total Points Scored (PTS), Percentage of Field Goals (FG%), Percentage of 2 Point Shots Made (2PT%),
Percentage of 3 Point Shots Made (3PT%)  for all the teams in the given PbP df.'''
    keep = (df['team_name'] != "")
    df= df[keep].dropna(how='all')

    team = df['team_name'].unique()  # numpy.array
    stats = pd.DataFrame({'TEAM': team}).set_index('TEAM')
    opp = pd.DataFrame({'TEAM': team}).set_index('TEAM')
    # Estadísticas basicas
    stats['AST'] = df[(df['actionType_x'] == 'assist')].groupby('team_name', sort=True)['actionType_x'].count()
    stats['STL'] = df[(df['actionType_x'] == 'steal')].groupby('team_name', sort=True)['actionType_x'].count()
    stats['BLK'] = df[(df['actionType_x'] == 'block')].groupby('team_name', sort=True)['actionType_x'].count()

    stats['2PTA'] = df[(df['actionType_x'] == '2pt')].groupby('team_name', sort=True)['actionType_x'].count()
    stats['2PT'] = df[((df['actionType_x'] == '2pt') & (df['success'] == 1))].groupby('team_name', sort=True)[
        'actionType_x'].count()

    stats['3PTA'] = df[(df['actionType_x'] == '3pt')].groupby('team_name', sort=True)['actionType_x'].count()
    stats['3PT'] = df[((df['actionType_x'] == '3pt') & (df['success'] == 1))].groupby('team_name', sort=True)[
        'actionType_x'].count()

    stats['FTA'] = df[(df['actionType_x'] == 'freethrow')].groupby('team_name', sort=True)['actionType_x'].count()
    stats['OppFTA'] = df[(df['actionType_x'] == 'freethrow')].groupby('team_rival', sort=True)['actionType_x'].count()
    stats['FT'] = df[((df['actionType_x'] == 'freethrow') & (df['success'] == 1))].groupby('team_name', sort=True)[
        'actionType_x'].count()

    stats['ORB'] = \
    df[((df['actionType_x'] == 'rebound') & (df['subType_x'] == 'offensive'))].groupby('team_name', sort=True)[
        'actionType_x'].count()
    stats['DRB'] = \
    df[((df['actionType_x'] == 'rebound') & (df['subType_x'] == 'defensive'))].groupby('team_name', sort=True)[
        'actionType_x'].count()

    stats['OppDRB'] = \
    df[((df['actionType_x'] == 'rebound') & (df['subType_x'] == 'defensive'))].groupby('team_rival', sort=True)[
        'actionType_x'].count()
    stats['OppORB'] = \
    df[((df['actionType_x'] == 'rebound') & (df['subType_x'] == 'offensive'))].groupby('team_rival', sort=True)[
        'actionType_x'].count()

    stats['TO'] = df[(df['actionType_x'] == 'turnover')].groupby('team_name', sort=True)['actionType_x'].count()
    stats['OppTO'] = df[(df['actionType_x'] == 'turnover')].groupby('team_rival', sort=True)['actionType_x'].count()

    stats['Opp3PT'] = df[((df['actionType_x'] == '3pt') & (df['success'] == 1))].groupby('team_rival', sort=True)[
        'actionType_x'].count()

    stats['FGA'] = df[(df['actionType_x'].isin(['2pt', '3pt']))].groupby('team_name', sort=True)[
        'actionType_x'].count()
    stats['OppFGA'] = df[(df['actionType_x'].isin(['2pt', '3pt']))].groupby('team_rival', sort=True)[
        'actionType_x'].count()

    stats['FG'] = \
    df[(df['actionType_x'].isin(['2pt', '3pt']) & (df['success'] == 1))].groupby('team_name', sort=True)[
        'actionType_x'].count()
    stats['OppFG'] = \
    df[(df['actionType_x'].isin(['2pt', '3pt']) & (df['success'] == 1))].groupby('team_rival', sort=True)[
        'actionType_x'].count()

    stats.fillna(0, inplace=True)  # por el boolean mask
    opp.fillna(0, inplace=True)
    # Attempted and Made Points
    # stats['PTSA'] = 3 * stats['3PTA'] + 2 * stats['2PTA'] + stats['FTA']
    stats['PTS'] = 3 * stats['3PT'] + 2 * stats['2PT'] + stats['FT']
    # Percentage of Field Goals Made
    stats['FG%'] = stats['FG'] / stats['FGA'] * 100
    # Ppercentage of 2 point shots made
    stats['2PT%'] = stats['2PT'] / stats['2PTA'] * 100
    # Percentage of 3 point shots made
    stats['3PT%'] = stats['3PT'] / stats['3PTA'] * 100

    #### FOUR FACTORS
    ## SHOOTING:
    # Effective Field Goal Percentage
    # This measure is a scale corrected measure to identify field goal percentage for a team.
    # With eFG% we do obtain the best relative measurement for points per field goal attempt; simple by multiplying by two.
    # accounts for made three pointers (3PM). isolates a player’s (or team’s) shooting efficiency from the field.
    stats['eFG%'] = (stats['FG'] + 0.5 * stats['3PT']) / stats['FGA']
    stats['OppeFG%'] = (stats['OppFG'] + 0.5 * stats['Opp3PT']) / stats['OppFGA']

    # True Shooting Percentage
    # accounts for both three pointers and free throws.
    # Provides a measure of total efficiency in scoring attempts, takes into account field goals, 3-point field goals and free throws.
    stats['TS%'] = (stats['PTS'] / 2) / (stats['FGA'] + 0.44 * stats['FTA'])

    ## REBOUNDINGS: ORBP, DRBP (offensive and Defensive Rebound Percentage)
    stats['DREB%'] = stats['DRB'] / (stats['DRB'] + stats['OppORB'])
    stats['OREB%'] = stats['ORB'] / (stats['ORB'] + stats['OppDRB'])

    ## TURNOVER: Turnover Ratio
    # Turnover percentage is an estimate of turnovers per plays. ( play = FGA + 0.44 * FTA + TO ) La definición de la NBA incluye AST en denominador
    stats['TOV%'] = stats['TO'] / (stats['FGA'] + 0.44 * stats['FTA'] + stats['TO'])
    stats['OppTOV%'] = stats['OppTO'] / (stats['OppFGA'] + 0.44 * stats['OppFTA'] + stats['OppTO'])

    ## FREE THROWS:
    # Field Throw Attempt
    stats['FTRate'] = stats['FTA'] / stats['FGA']
    stats['OppFTRate'] = stats['OppFTA'] / stats['OppFGA']

    return stats


# ----------------------------------------------------------------------
# Database connection
# connect_string = 'mysql+mysqlconnector://agmm23:mysqlpassword1a@agmm23.mysql.pythonanywhere-services.com/agmm23$xcouter_db'
connect_string = 'mysql+mysqlconnector://root:password@localhost/xcouter_lub_fem_2020'

sql_engine = sql.create_engine(connect_string)
query = "select * from playbyplay" #Todo Cambiar la query por una de alchemy



# ----------------------------------------------------------------------
# App Layout
#app = Flask(__name__)

app = dash.Dash(__name__, prevent_initial_callbacks=True)


#Preparar data
df = pd.read_sql_query(query, sql_engine)

stats_df = calcular_stats_x_team(df)

stats_df.reset_index(inplace=True)


app.layout = html.Div([
    html.H1('Equipo Local'),
    dcc.Dropdown(
        id='dropdown-team-local',
        options=[{'label': k, 'value': k} for k in all_team_players.keys()],
        value=all_teams[0]
    ),
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