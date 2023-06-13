import pickle

with open('logs_games.pickle', 'rb') as f:
    logs = pickle.load(f)

print(logs[4:5].to_string())