import pandas as pd

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