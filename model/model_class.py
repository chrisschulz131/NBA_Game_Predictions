from nba_api.stats.static import teams
from sklearn import linear_model
import pandas as pd


class Model:
    """
    this class will handle everything related to pre-processing data, model training, creation, and prediction.
    """
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)
        self.model = linear_model.LinearRegression()
        # having the team abbreviations and their mapped encoding is a good idea.
        self.team_abbvs_dict = self.get_team_num_vals()

    def preprocess(self):
        """
        """
        self.encode_teams()
        self.encode_wins_losses()
        self.df.to_csv("encoded-stats.csv", index=False)

    def encode_teams(self):
        """
        We need to encode our teams because sci kit learn doesn't want text.
        The teams will be encoded alphabetically from 0-29
        """

        for abbv in self.team_abbvs_dict:
            self.df['HOME_ABRV'] = self.df['HOME_ABRV'].replace(abbv, str(self.team_abbvs_dict[abbv]))
            self.df['AWAY_ABRV'] = self.df['AWAY_ABRV'].replace(abbv, str(self.team_abbvs_dict[abbv]))

    def encode_wins_losses(self):
        """
        Wins = 1, Losses = 0
        """
        self.df['HOME_WL'] = self.df['HOME_WL'].replace("W", "1")
        self.df['HOME_WL'] = self.df['HOME_WL'].replace("L", "0")

    def get_team_num_vals(self):

        team_abbvs_dict = {}
        team_info = teams.get_teams()

        for team in range(0, len(team_info)):
            team_abbvs_dict[team_info[team]['abbreviation']] = team

        return team_abbvs_dict
