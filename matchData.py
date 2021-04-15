
import numpy as np
import pandas as pd
import datetime as dt
import requests
import json
import time

totalHeroes = 129

class Match(object):
    def __init__(self, match_id = '', radiant_win = False, radiant = [], dire = []):
        self.match_id = match_id
        self.radiant_win = radiant_win
        self.radiant = radiant
        self.dire = dire

def forge(newest, oldest, n):
    difference = newest - oldest
    increment = difference / n
    intervals = []
    for i in range(n):
        intervals.append(oldest + i * increment)
    return intervals

def request(url):
    response = requests.get(url)
    return response.json()

def getMatchData(apicall):
    matches = request(apicall)
    radiant, dire, games = [], [], []

    try:
        for row in matches['rows']:
            match_id = row['match_id']
            radiant_win = row['radiant_win']
            if (row['player_slot'] < 100):
                radiant.append(row['hero_id'])
            else:
                dire.append(row['hero_id'])

            if len(radiant) == len(dire) == 5:
                game = Match(match_id, radiant_win, radiant, dire)
                radiant = []
                dire = []
                games.append(game)

        with open('matches.csv', 'a') as f:
            for game in games:
                for i in range(1, totalHeroes+1):
                    if i in game.radiant:
                        f.write('1.0,')
                    elif i in game.dire:
                        f.write('-1.0,')
                    else:
                        f.write('0.0,')
                if game.radiant_win == True:
                    f.write('1')
                else:
                    f.write('0')
                f.write('\n')
    except:
        time.sleep(3)
        print('blargh')

def runQueries(intervals):
    for i in range(n-1):
        time.sleep(3)
        sql = """SELECT public_matches.match_id, radiant_win, player_slot, hero_id 
        FROM public_matches JOIN public_player_matches ON public_matches.match_id = public_player_matches.match_id 
        WHERE 3000 < avg_mmr AND avg_mmr < 5000 AND start_time > %i AND start_time < %i AND lobby_type = 7 AND game_mode = 22 
        LIMIT 10000""" % (int(intervals[i]), int(intervals[i + 1]))

        getMatchData('https://api.opendota.com/api/explorer?sql=' + sql)
        print('Query ' + str(i+1) + ' of ' + str(n-1) + ' completed')

def calcAllWinrates():
    matches = pd.read_csv('matches.csv', sep=',', header=None)
    matches = matches.values
    print("loaded matches.csv!")
    wins = np.zeros((totalHeroes, totalHeroes))

    for i in range(matches.shape[0]):
        radiant = []
        dire = []
        row = matches[i]

        for j in range(totalHeroes):
            if (row[j] == 1.0):
                radiant.append(j)
            elif (row[j] == -1.0):
                dire.append(j)

        if (len(radiant) != 5 or len(dire) != 5):
            print("bad team comp!! not = 5")
            print(len(radiant))
            print(len(dire))

        winners = []
        losers = []

        if (row[totalHeroes] == 1.0):
            winners = radiant
            losers = dire
        elif (row[totalHeroes] == 0.0):
            winners = dire
            losers = radiant
        else:
            print("no victor! something wrong")

        for winnerId in winners:
            for loserId in losers:
                wins[winnerId][loserId] += 1

    percents = np.zeros((totalHeroes, totalHeroes))
    for i in range(totalHeroes):
        for j in range(totalHeroes):
            if i != j:
                percents[i][j] = wins[i][j]/(wins[i][j] + wins[j][i])
                percents[j][i] = wins[j][i]/(wins[i][j] + wins[j][i])

    np.savetxt("winrates.csv", percents, delimiter=",")
    print("saved winrates to winrates.csv!")

if __name__ == '__main__':
    newest = dt.datetime(2019,9,17,0,0).timestamp()
    oldest = dt.datetime(2019,9,1,0,0).timestamp()

    n = 100
    intervals = forge(newest, oldest, n)

    #runQueries(intervals)

    calcAllWinrates()