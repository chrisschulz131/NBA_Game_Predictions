from nba_api.stats.static import teams
from sklearn import linear_model, model_selection
import pandas as pd


class Model:
    """
    this class will handle everything related to pre-processing data, model training, creation, and prediction.
    """
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)
        self.model = linear_model.LogisticRegression(max_iter=2000)
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
        print(team_info)

        for team in range(0, len(team_info)):
            team_abbvs_dict[team_info[team]['abbreviation']] = team

        print(team_abbvs_dict)

        return team_abbvs_dict

    def train_model(self):

        self.df.drop(columns=["GAME_DATE", "MATCHUP", "TEAM_ID", "HOME_PTS", "AWAY_PTS"], inplace=True)
        y_vals = self.df[['HOME_WL']]
        self.df.drop(columns="HOME_WL", inplace=True)
        X_train, X_test, y_train, y_test = model_selection.train_test_split(self.df, y_vals, test_size=0.25)
        self.model.fit(X_train, y_train.values.ravel())

        # todo write method in data scraper to get today's games and put it in a csv file.
        tonights_games = pd.read_csv('data_scraping/tonights_games.csv')

        # todo run this 10,000 times and average out the predictions
        print(self.model.predict_proba(tonights_games))

