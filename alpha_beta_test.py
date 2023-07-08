import pickle
from modelisation.Entities import *

with open("modelisation/logs_games.pickle", 'rb') as f:
    test = pickle.load(f).to_dict(orient='index')
