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
        # todo: add functionality for multiple seasons...focused on getting it working with one season for now.
        self.seasons = "2019-20" if seasons is None else seasons
        self.team_info = None

    def get_teams(self):
        """
        method to get all nba teams using the NBA api.
        """
        self.team_info = teams.get_teams()
        for team in self.team_info:
            # we have to sleep when making requests or we'll get booted.
            time.sleep(5)
            temp_frame = leaguegamefinder.LeagueGameFinder(team_id_nullable=team['id'],
                                                           season_nullable=self.seasons).get_data_frames()[0]
            self.df = self.df.append(temp_frame, ignore_index=True)

        # drop the columns we don't need.
        self.df.drop(columns=['FGM', 'FGA', 'MIN', 'FG3M', 'FG3A', 'FTM', 'FTA', 'PLUS_MINUS', 'TEAM_NAME',
                              'GAME_DATE'], inplace=True)

    def determine_home_away(self):
        """
        Method to determine who was home and who was away.
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

                # manually encode our team abbreviations
                # team['TEAM_ABBREVIATION'] = team['TEAM_ABBREVIATION'].replace(team['TEAM_ABBREVIATION'],
                #                                                               str(team_abbvs_dict.get(team['TEAM_ABBREVIATION'])))
            else:
                self.df.drop(matching_game_id.index, inplace=True)

        self.df['HOME_PTS'] = home_points
        self.df['AWAY_PTS'] = away_points

        # reorder columns to make a little more sense
        self.df = self.df[["SEASON_ID", "TEAM_ID", "TEAM_ABBREVIATION", "GAME_ID", "MATCHUP", "HOME_TEAM",
                           "HOME_PTS", "AWAY_TEAM", "AWAY_PTS", "WL", "PTS", "FG_PCT", "FG3_PCT",
                           "FT_PCT", "OREB", "DREB", "REB", "AST", "STL", "BLK", "TOV", "PF"]]

    def save_as_csv(self):
        self.df.to_csv(self.seasons + "-stats", index=False)


if __name__ == '__main__':
    # todo: eventually I can make this take command line arguments
    scrape_obj = Scraper(None)
    scrape_obj.get_teams()
    scrape_obj.determine_home_away()
    scrape_obj.save_as_csv()
