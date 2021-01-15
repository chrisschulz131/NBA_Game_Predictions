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

    def encode_teams(self):
        """
        We need to encode our teams because sci kit learn doesn't want text.
        The teams will be encoded alphabetically from 0-29
        """

        for abbv in self.team_abbvs_dict:
            self.df['TEAM_ABBREVIATION'] = self.df['TEAM_ABBREVIATION'].replace(abbv, str(self.team_abbvs_dict[abbv]))
            self.df['HOME_TEAM'] = self.df['HOME_TEAM'].replace(abbv, str(self.team_abbvs_dict[abbv]))
            self.df['AWAY_TEAM'] = self.df['AWAY_TEAM'].replace(abbv, str(self.team_abbvs_dict[abbv]))

    def encode_wins_losses(self):
        """
        Wins = 1, Losses = 0
        """
        raise NotImplementedError

    def get_team_num_vals(self):

        team_abbvs_dict = {}
        team_abbvs = sorted(self.df.TEAM_ABBREVIATION.unique())
        for team in range(0, len(team_abbvs)):
            team_abbvs_dict[team_abbvs[team]] = team

        return team_abbvs_dict
