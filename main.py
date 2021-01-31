"""
This class will end up being the script to run the whole project.
"""
import pandas as pd
from sklearn import linear_model
from sklearn.preprocessing import LabelEncoder, OrdinalEncoder
from sklearn.compose import ColumnTransformer
from model.model_class import Model

if __name__ == '__main__':

    model = Model('data_scraping/2019-20-stats.csv')
    # preprocess will encode the teams and WL columns
    model.preprocess()



