from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import teamgamelogs
from nba_api.stats.library.parameters import SeasonAll
from nba_api.stats.endpoints import leaguegamefinder, boxscoreadvancedv2, boxscoretraditionalv2
import pandas as pd
import time


# Todo: restructure this, specifically break it down more... pass in desired seasons as a parameter

"""
Collecting nba game results and preparing it / altering it to be entered into ML algo's
"""

teams_data_frame = pd.DataFrame()
team_dict = teams.get_teams()
for team in team_dict:
    time.sleep(5)
    df = leaguegamefinder.LeagueGameFinder(team_id_nullable=team['id'], season_nullable="2019-20").get_data_frames()[0]
    teams_data_frame = teams_data_frame.append(df, ignore_index=True)

teams_data_frame.drop(columns=['FGM', 'FGA', 'MIN', 'FG3M', 'FG3A', 'FTM', 'FTA', 'PLUS_MINUS', 'TEAM_NAME',
                               'GAME_DATE'], inplace=True)

home_teams = []
away_teams = []

for index, team in teams_data_frame.iterrows():
    versus = team['MATCHUP'].split(" ")
    print(versus)
    if versus[1] == "vs.":
        home_teams.append(versus[0])
        away_teams.append(versus[2])
    else:
        home_teams.append(versus[2])
        away_teams.append(versus[0])

# add columns to show who was home and who was away.
teams_data_frame['HOME_TEAM'] = home_teams
teams_data_frame['AWAY_TEAM'] = away_teams

home_points = []
away_points = []
for index, team in teams_data_frame.iterrows():
    game_id = team['GAME_ID']
    matching_game_id = teams_data_frame.loc[teams_data_frame['GAME_ID'] == game_id]
    if len(matching_game_id) == 2:
        print(type(matching_game_id))
        print(matching_game_id)
        if team['TEAM_ABBREVIATION'] == team['HOME_TEAM']:
            home_points.append(int(team['PTS']))
            away_points.append(int(matching_game_id.iloc[[1]]['PTS']))
        else:
            home_points.append(int(matching_game_id.iloc[[1]]['PTS']))
            away_points.append(int(team['PTS']))
    else:
        teams_data_frame.drop(matching_game_id.index, inplace=True)

teams_data_frame['HOME_PTS'] = home_points
teams_data_frame['AWAY_PTS'] = away_points

# reorder columns to make a little more sense
teams_data_frame = teams_data_frame[["SEASON_ID", "TEAM_ID", "TEAM_ABBREVIATION", "GAME_ID", "MATCHUP", "HOME_TEAM",
                                     "HOME_PTS", "AWAY_TEAM", "AWAY_PTS", "WL","PTS", "FG_PCT", "FG3_PCT",
                                     "FT_PCT", "OREB", "DREB", "REB", "AST", "STL", "BLK", "TOV", "PF"]]

teams_data_frame.to_csv('nba_stats.csv', index=False)



