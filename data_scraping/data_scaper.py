from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import teamgamelogs
from nba_api.stats.library.parameters import SeasonAll
from nba_api.stats.endpoints import leaguegamefinder, boxscoreadvancedv2, boxscoretraditionalv2
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import time


class Scraper:
    """
    A class to scrape box score data from the given list of seasons.
    """
    def __init__(self, seasons):
        self.df = pd.DataFrame()
        self.away_stats = pd.DataFrame()
        # todo: add functionality for multiple seasons...focused on getting it working with one season for now.
        self.seasons = "2019-20" if seasons is None else seasons
        self.team_info = None

    def get_teams(self):
        """
        method to get all nba teams using the NBA api and create data frame with box scores.
        """
        self.team_info = teams.get_teams()
        for team in self.team_info:
            # we have to sleep when making requests or we'll get booted.
            time.sleep(5)
            temp_frame = leaguegamefinder.LeagueGameFinder(team_id_nullable=team['id'],
                                                           season_nullable=self.seasons).get_data_frames()[0]

            self.df = self.df.append(temp_frame, ignore_index=True)

        # drop the columns we don't need.
        self.df.drop(columns=['FGM', 'FGA', 'MIN', 'FG3M', 'FG3A', 'FTM', 'FTA', 'PLUS_MINUS', 'TEAM_NAME', 'REB'], inplace=True)

    def determine_home_away(self):
        """
        Method to determine who was home and who was away. This add's the away team's stats.
        Also matches the points to the home/away team
        """
        home_teams = []
        away_teams = []

        for index, team in self.df.iterrows():
            versus = team['MATCHUP'].split(" ")
            if versus[1] == "vs.":
                home_teams.append(versus[0])
                away_teams.append(versus[2])
            else:
                home_teams.append(versus[2])
                away_teams.append(versus[0])

        self.df['HOME_TEAM'] = home_teams
        self.df['AWAY_TEAM'] = away_teams

        home_points = []
        away_points = []
        for index, team in self.df.iterrows():
            game_id = team['GAME_ID']
            matching_game_id = self.df.loc[self.df['GAME_ID'] == game_id]
            if len(matching_game_id) == 2:
                if team['TEAM_ABBREVIATION'] == team['HOME_TEAM']:
                    home_points.append(int(team['PTS']))
                    away_points.append(int(matching_game_id.iloc[[1]]['PTS']))
                else:
                    home_points.append(int(matching_game_id.iloc[[1]]['PTS']))
                    away_points.append(int(team['PTS']))

                # add away team's stats to the away stats dataframe
                games = self.df.loc[(self.df['GAME_ID'] == game_id) & (self.df['HOME_TEAM'] != self.df['TEAM_ABBREVIATION'])]
                self.away_stats = self.away_stats.append(games.iloc[0])
            else:
                self.df.drop(matching_game_id.index, inplace=True)

        self.df['HOME_PTS'] = home_points
        self.df['AWAY_PTS'] = away_points
        self.away_stats = self.away_stats[["SEASON_ID", "TEAM_ID", "TEAM_ABBREVIATION", "GAME_ID", "GAME_DATE", "MATCHUP",
                                 "HOME_TEAM", "WL", "PTS", "FG_PCT", "FG3_PCT", "FT_PCT", "OREB", "DREB", "AST", "STL",
                                 "BLK", "TOV", "PF"]]

        self.away_stats.sort_values(by=['GAME_ID'], inplace=True)
        self.away_stats.drop_duplicates('GAME_ID', inplace=True)

        # rename away_stats columns in preparation for combining it with the home stats in self.df
        self.away_stats.rename(columns={"TEAM_ABBREVIATION": "AWAY_ABRV", "PTS": "AWAY_PTS", "FG_PCT": "AWAY_FG_PCT",
                                   "FG3_PCT": "AWAY_FG3_PCT", "FT_PCT": "AWAY_FT_PCT", "OREB": "AWAY_OREB",
                                   "DREB": "AWAY_DREB", "AST": "AWAY_AST", "STL": "AWAY_STL", "BLK": "AWAY_BLK",
                                   "TOV": "AWAY_TOV", "PF": "AWAY_PF"}, inplace=True)

        self.away_stats.drop(columns=["SEASON_ID", "TEAM_ID", "GAME_DATE", "MATCHUP", "HOME_TEAM", "WL"], inplace=True)

        # drop away games from original dataframe. Giving us two dataframes, one with home stats and one with away stats
        # for a given game.
        self.df = self.df.loc[self.df['HOME_TEAM'] == self.df['TEAM_ABBREVIATION']]

        # reorder columns to make a little more sense
        self.df = self.df[["SEASON_ID", "TEAM_ID", "TEAM_ABBREVIATION", "GAME_ID", "GAME_DATE", "MATCHUP",
                           "WL", "PTS", "FG_PCT", "FG3_PCT", "FT_PCT", "OREB", "DREB", "AST", "STL",
                           "BLK", "TOV", "PF"]]

        # rename home stats columns in preparation for combining it with the away stats
        self.df.rename(columns={"TEAM_ABBREVIATION": "HOME_ABRV", "WL": "HOME_WL", "PTS": "HOME_PTS",
                                "FG_PCT": "HOME_FG_PCT", "FG3_PCT": "HOME_FG3_PCT", "FT_PCT": "HOME_FT_PCT",
                                "OREB": "HOME_OREB", "DREB": "HOME_DREB", "AST": "HOME_AST", "STL": "HOME_STL",
                                "BLK": "HOME_BLK", "TOV": "HOME_TOV", "PF": "HOME_PF"}, inplace=True)

        self.df.sort_values(by=['GAME_ID'], inplace=True)
        self.df = pd.concat([self.df.set_index("GAME_ID"), self.away_stats.set_index("GAME_ID")],
                            axis=1)

    def save_as_csv(self):
        self.df.to_csv(self.seasons + "-stats.csv", index=False)
        self.away_stats.to_csv(self.seasons + "-away_stats.csv", index=False)


if __name__ == '__main__':
    # todo: eventually I can make this take command line arguments
    scrape_obj = Scraper(None)
    scrape_obj.get_teams()
    scrape_obj.determine_home_away()
    scrape_obj.save_as_csv()
