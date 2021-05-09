import pandas as pd
import plotly.graph_objects as go

def calcular_puntos(df):
    if df['success']==1 and df['actionType_x']=='3pt':
        return 3
    elif df['success']==1 and df['actionType_x']=='2pt':
        return 2
    elif df['success']==1 and df['actionType_x']=='freethrow':
        return 1
    else:
        return 0


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
    stats['2PTA%'] = stats['2PTA'] / stats['FGA'] * 100
    stats['3PTA%'] = stats['3PTA'] / stats['FGA'] * 100

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

#Toma los promedios de la tabla de la funcion calcular_stats_x_team y calcula las estadisticas para toda la liga
def calcular_estadisticas_liga(stats_df):
    league_stats = stats_df.sum(numeric_only=True)[['AST', 'STL', 'BLK', '2PTA', '2PT', '3PTA', '3PT', 'FTA', 'OppFTA',
                                                    'FT', 'ORB', 'DRB', 'OppDRB', 'OppORB', 'TO', 'OppTO', 'Opp3PT',
                                                    'FGA',
                                                    'OppFGA', 'FG', 'OppFG', 'PTS']]
    league_stats['FG%'] = league_stats['FG'] / league_stats['FGA'] * 100
    # Ppercentage of 2 point shots made
    league_stats['2PT%'] = league_stats['2PT'] / league_stats['2PTA'] * 100
    # Percentage of 3 point shots made
    league_stats['3PT%'] = league_stats['3PT'] / league_stats['3PTA'] * 100
    league_stats['2PTA%'] = league_stats['2PTA'] / league_stats['FGA'] * 100
    league_stats['3PTA%'] = league_stats['3PTA'] / league_stats['FGA'] * 100

    #### FOUR FACTORS
    ## SHOOTING:
    # Effective Field Goal Percentage
    # This measure is a scale corrected measure to identify field goal percentage for a team.
    # With eFG% we do obtain the best relative measurement for points per field goal attempt; simple by multiplying by two.
    # accounts for made three pointers (3PM). isolates a player’s (or team’s) shooting efficiency from the field.
    league_stats['eFG%'] = (league_stats['FG'] + 0.5 * league_stats['3PT']) / league_stats['FGA']
    league_stats['OppeFG%'] = (league_stats['OppFG'] + 0.5 * league_stats['Opp3PT']) / league_stats['OppFGA']

    # True Shooting Percentage
    # accounts for both three pointers and free throws.
    # Provides a measure of total efficiency in scoring attempts, takes into account field goals, 3-point field goals and free throws.
    league_stats['TS%'] = (league_stats['PTS'] / 2) / (league_stats['FGA'] + 0.44 * league_stats['FTA'])

    ## REBOUNDINGS: ORBP, DRBP (offensive and Defensive Rebound Percentage)
    league_stats['DREB%'] = league_stats['DRB'] / (league_stats['DRB'] + league_stats['OppORB'])
    league_stats['OREB%'] = league_stats['ORB'] / (league_stats['ORB'] + league_stats['OppDRB'])

    ## TURNOVER: Turnover Ratio
    # Turnover percentage is an estimate of turnovers per plays. ( play = FGA + 0.44 * FTA + TO ) La definición de la NBA incluye AST en denominador
    league_stats['TOV%'] = league_stats['TO'] / (league_stats['FGA'] + 0.44 * league_stats['FTA'] + league_stats['TO'])
    league_stats['OppTOV%'] = league_stats['OppTO'] / (
                league_stats['OppFGA'] + 0.44 * league_stats['OppFTA'] + league_stats['OppTO'])

    ## FREE THROWS:
    # Field Throw Attempt
    league_stats['FTRate'] = league_stats['FTA'] / league_stats['FGA']
    league_stats['OppFTRate'] = league_stats['OppFTA'] / league_stats['OppFGA']
    league_stats = pd.DataFrame(league_stats).T
    league_stats['TEAM'] = 'PROMEDIO_LIGA'
    cols = league_stats.columns.tolist()
    cols.insert(0, cols.pop(cols.index('TEAM')))
    league_stats = league_stats.reindex(columns=cols)

    return league_stats

def player_stats_df(df):
    '''stats_df: This function returns the Assists (AST), Steals (STL), Blocks (BLK), Offensive Rebounds (ORB), Defensive Rebounds (DRB), Opponent ORB (OppORB), Opponent DRB (OppDRB), Turnovers (TO), Opponent Turnovers (OppTO),
Free Throw Attempts (FTA), Free Throws Made (FT), 2 Point Shot Attempts (2PTA), 2 Point Shots Made (2PT), 3 Point Shot Attempts (3PTA), 3 Point Shots Made (3PT),
Field Goal Attempted (FGA), Field Goals Made (FG), Total Points Scored (PTS), Percentage of Field Goals (FG%), Percentage of 2 Point Shots Made (2PT%),
Percentage of 3 Point Shots Made (3PT%)  for every player in team given PbP df.'''
    keep = (df['player_x'] != "")
    df= df[keep].dropna(how='all') #borro entradas con team vacio

    df['player'] = (df['internationalFamilyName'] + ', ' + df['internationalFirstName']).str.upper()

    #team = pd.unique(df[['team_name', 'team_rival']].values.ravel())

    player = df['player'].dropna().unique()  # numpy.array - creo primer columna de los df

    #player = df[df['team_name'] == team]['player'].unique()

    stats = pd.DataFrame({'PLAYER': player}).set_index('PLAYER')

    #opp = pd.DataFrame({'PLAYER': player}).set_index('PLAYER')
    # MATCHES
    #stats['TEAM'] = df.groupby('team_name').groups.keys()
    #stats['TEAM'] = df.groupby('player')[['team_name']].unique()




    # Estadísticas basicas
    stats['AST'] = df[(df['actionType_x'] == 'assist')].groupby('player', sort=True)['actionType_x'].count()
    stats['STL'] = df[(df['actionType_x'] == 'steal')].groupby('player', sort=True)['actionType_x'].count()
    stats['BLK'] = df[(df['actionType_x'] == 'block')].groupby('player', sort=True)['actionType_x'].count()

    stats['2PTA'] = df[(df['actionType_x'] == '2pt')].groupby('player', sort=True)['actionType_x'].count()
    stats['2PT'] = df[((df['actionType_x'] == '2pt') & (df['success'] == 1))].groupby('player', sort=True)[
        'actionType_x'].count()

    stats['3PTA'] = df[(df['actionType_x'] == '3pt')].groupby('player', sort=True)['actionType_x'].count()
    stats['3PT'] = df[((df['actionType_x'] == '3pt') & (df['success'] == 1))].groupby('player', sort=True)[
        'actionType_x'].count()

    stats['FTA'] = df[(df['actionType_x'] == 'freethrow')].groupby('player', sort=True)['actionType_x'].count()
    #stats['OppFTA'] = df[(df['actionType'] == 'freethrow') & (df['team_rival'] == team)].groupby('player', sort=True)['actionType'].count()
    stats['FT'] = df[((df['actionType_x'] == 'freethrow') & (df['success'] == 1))].groupby('player', sort=True)[
        'actionType_x'].count()

    stats['ORB'] = \
    df[((df['actionType_x'] == 'rebound') & (df['subType_x'] == 'offensive'))].groupby('player', sort=True)[
        'actionType_x'].count()
    stats['DRB'] = \
    df[((df['actionType_x'] == 'rebound') & (df['subType_x'] == 'defensive'))].groupby('player', sort=True)[
        'actionType_x'].count()


    #stats['OppDRB'] = \
    #df[((df['actionType'] == 'rebound') & (df['subType'] == 'defensive') & (df['team_rival'] == team))].groupby('player', sort=True)[
    #    'actionType'].count()
    #stats['OppORB'] = \
    #df[((df['actionType'] == 'rebound') & (df['subType'] == 'offensive') & (df['team_rival'] == team))].groupby('player', sort=True)[
    #    'actionType'].count()

    stats['TO'] = df[(df['actionType_x'] == 'turnover')].groupby('player', sort=True)['actionType_x'].count()
    #stats['OppTO'] = df[(df['actionType'] == 'turnover') & (df['team_rival'] == team)].groupby('player', sort=True)['actionType'].count()

    #stats['Opp3PT'] = df[((df['actionType'] == '3pt') & (df['success'] == 1) & (df['team_rival'] == team))].groupby('player', sort=True)[
    #    'actionType'].count()

    stats['FGA'] = df[(df['actionType_x'].isin(['2pt', '3pt']))].groupby('player', sort=True)[
        'actionType_x'].count()
    #stats['OppFGA'] = df[(df['actionType'].isin(['2pt', '3pt']) & (df['team_rival'] == team))].groupby('player', sort=True)[
    #    'actionType'].count()

    stats['FG'] = \
    df[(df['actionType_x'].isin(['2pt', '3pt']) & (df['success'] == 1))].groupby('player', sort=True)[
        'actionType_x'].count()
    #stats['OppFG'] = \
    #df[(df['actionType'].isin(['2pt', '3pt']) & (df['success'] == 1) & (df['team_rival'] == team))].groupby('player', sort=True)[
    #    'actionType'].count()

    stats.fillna(0, inplace=True)  # por el boolean mask
    #opp.fillna(0, inplace=True)
    # Attempted and Made Points
    # stats['PTSA'] = 3 * stats['3PTA'] + 2 * stats['2PTA'] + stats['FTA']
    stats['PTS'] = 3 * stats['3PT'] + 2 * stats['2PT'] + stats['FT']
    # Percentage of Field Goals Made
    stats['FG%'] = (stats['FG'] / stats['FGA'] * 100).fillna('0')

    # Percentage of 2 point shots made
    # fillna with 0 - when no 2PTS where made (divide by zero)
    stats['2PT%'] = (stats['2PT'] / stats['2PTA'] * 100).fillna('0')
    # Percentage of 3 point shots made
    #stats['3PT%'] = stats['3PT'] / stats['3PTA'] * 100
    # fillna with 0 - when no 3PTS where made
    stats['3PT%'] = (stats['3PT'] / stats['3PTA'] * 100).fillna('0')
    #stats['3PT%'] = stats['3PT'].div(stats['3PTA']).replace(NaN, 0) * 100

    #Points per shot attempt
    #is a player efficiency evaluation metric which is calculated by dividing the total points (2P made and 3P made) by the total field goals attempts.
    # https://www.nbastuffer.com/analytics101/points-per-shot-attempt/

    stats['PPSA'] = (( 2 * stats['2PT'] + 3 * stats['3PT'] ) / stats['FGA']).fillna('0')

    #### FOUR FACTORS
    ## SHOOTING:
    # Effective Field Goal Percentage
    # This measure is a scale corrected measure to identify field goal percentage for a team.
    # With eFG% we do obtain the best relative measurement for points per field goal attempt; simple by multiplying by two.
    # accounts for made three pointers (3PM). isolates a player’s (or team’s) shooting efficiency from the field.
    stats['eFG%'] = ((stats['FG'] + 0.5 * stats['3PT']) / stats['FGA']).fillna('0')
    #stats['OppeFG%'] = (stats['OppFG'] + 0.5 * stats['Opp3PT']) / stats['OppFGA']

    # True Shooting Percentage
    # accounts for both three pointers and free throws.
    # Provides a measure of total efficiency in scoring attempts, takes into account field goals, 3-point field goals and free throws.
    stats['TS%'] = ((stats['PTS'] / 2) / (stats['FGA'] + 0.44 * stats['FTA'])).fillna('0')

    ## REBOUNDINGS: ORBP, DRBP (offensive and Defensive Rebound Percentage)
    #stats['DREB%'] = stats['DRB'] / (stats['DRB'] + stats['OppORB'])
    #stats['OREB%'] = stats['ORB'] / (stats['ORB'] + stats['OppDRB'])

    ## TURNOVER: Turnover Ratio
    # Turnover percentage is an estimate of turnovers per plays. ( play = FGA + 0.44 * FTA + TO ) La definición de la NBA incluye AST en denominador
    stats['TOR%'] = (stats['TO'] / (stats['FGA'] + 0.44 * stats['FTA'] + stats['TO'])).fillna('0')
    #stats['OppTOR%'] = stats['OppTO'] / (stats['OppFGA'] + 0.44 * stats['OppFTA'] + stats['OppTO'])

    ## FREE THROWS:
    # Free Throw Attempt
    stats['FTRate'] = (stats['FTA'] / stats['FGA']).fillna('0')
    #stats['OppFTRate'] = stats['OppFTA'] / stats['OppFGA']

    #MATCHES
    stats['MATCHES'] = df.groupby('player')['id_match'].nunique()



    return stats.sort_values(by=['PLAYER'])

    #[['AST', 'STL', 'BLK', '2PTA', '2PT', '3PTA', '3PT%', 'FTA', 'FT', 'TO', 'ORB', 'DRB', 'FGA', 'FG']]

#print(stats_df.__doc__)


def x_player_stats_df(df, player): #dado df de stat, filtro por player
    #stats = pd.DataFrame({'TEAM': team}).set_index('TEAM') versión original
    stats = df.loc[[player]]
    return stats

def x_team_stats_df(df, team): #dado df de stat, filtro por player
    #stats = pd.DataFrame({'TEAM': team}).set_index('TEAM') versión original
    stats = df[df['team_name'] == team]
    return stats


def agregar_team_a_statsxplayer(player_stats_df, playbyplay_df):
    player_stats_df = player_stats_df.reset_index()

    keep = (playbyplay_df['player_x'] != "")
    playbyplay_df = playbyplay_df[keep].dropna(how='all')  # borro entradas con team vacio

    playbyplay_df['player'] = (
                playbyplay_df['internationalFamilyName'] + ', ' + playbyplay_df['internationalFirstName']).str.upper()
    grouped = playbyplay_df.groupby(['player', 'team_name']).count()
    grouped = grouped.reset_index()
    result = grouped[['player', 'team_name']]

    new_df = pd.merge(result, player_stats_df, how='left', left_on='player', right_on='PLAYER')
    new_df = new_df.drop('PLAYER', 1)

    return new_df

def obtener_df_para_tablas(df, team, column):
    df = df[df['team_name'] == team]
    df_result = df[['player', column]]
    return df_result


#GRAFICOS----------------------------------------------------------------------------------------------------

def Grafico_barras_acumulado_2(stats_df_league_added, selected_team, bar1_df, bar2_df, name_bar1, name_bar2):
    index_team = stats_df_league_added[stats_df_league_added['TEAM'] == selected_team].index[0]
    index_promedio_liga = stats_df_league_added[stats_df_league_added['TEAM'] == 'PROMEDIO_LIGA'].index[0]

    colors2pts = ['gainsboro', ] * len(stats_df_league_added['TEAM'])
    colors3pts = ['grey', ] * len(stats_df_league_added['TEAM'])
    colors2pts[index_team] = 'coral'
    colors3pts[index_team] = 'cornflowerblue'
    colors2pts[index_promedio_liga] = 'coral'
    colors3pts[index_promedio_liga] = 'cornflowerblue'

    graf_bar_acum2 = go.Figure(data=[
        go.Bar(name=name_bar1, x=stats_df_league_added['TEAM'], y=stats_df_league_added[bar1_df], marker_color=colors3pts),
        go.Bar(name=name_bar2, x=stats_df_league_added['TEAM'], y=stats_df_league_added[bar2_df], marker_color=colors2pts),

    ])

    graf_bar_acum2.update_layout(barmode='stack')

    return graf_bar_acum2

def Grafico_barras_simple(stats_df_league_added, selected_team, bar_df, name_bar):

    # stats_df_league_added.sort_values(by=[bar_df], inplace=True)
    #     #
    #     # stats_df_league_added.reset_index(drop=True)

    index_team = stats_df_league_added[stats_df_league_added['TEAM'] == selected_team].index[0]
    index_promedio_liga = stats_df_league_added[stats_df_league_added['TEAM'] == 'PROMEDIO_LIGA'].index[0]

    color_barras = ['gainsboro', ] * len(stats_df_league_added['TEAM'])
    color_barras[index_team] = 'coral'
    color_barras[index_promedio_liga] = 'cornflowerblue'

    graf_barras = go.Figure(data=[
        go.Bar(name=name_bar, x=stats_df_league_added['TEAM'], y=stats_df_league_added[bar_df],
               marker_color=color_barras)
    ])
    graf_barras.update_layout(xaxis={'categoryorder': 'total descending'})

    return graf_barras

def Grafico_barras_simple_players(df, bar_df, name_bar):

    graf_barras = go.Figure(data=[
        go.Bar(name=name_bar, x=df['player'], y=df[bar_df],
               marker_color='cornflowerblue')
    ])

    graf_barras.update_layout(xaxis={'categoryorder': 'total descending'})

    return graf_barras

