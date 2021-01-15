import pandas as pd


class Model:
    """
    this class will handle everything related to pre-processing data, model training, creation, and prediction.
    """
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)

    def preprocess(self):
        """
        """
        raise NotImplementedError

    def encode_teams(self):
        """
        we need to encode our teams because sci kit learn doesn't want text
        """

        raise NotImplementedError



