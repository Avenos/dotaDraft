
import numpy as np
import requests
import json
import time
import pandas as pd

totalHeroes = 129

class Hero(object):
    def __init__(self, name = '', ID = 0, winrate = 0.0):
        self.name = name
        self.ID = ID

def request(url):
    response = requests.get(url)
    return response.json()

#returns the ID for a particular hero name
def getID(heroname, herolist):
    allHeroNames = [x.name for x in herolist]
    idx = allHeroNames.index(heroname)
    return herolist[idx].ID

#returns the name for a particular hero ID
def getName(heroID, herolist):
    allHeroIDs = [x.ID for x in herolist]
    idx = allHeroIDs.index(heroID)
    return herolist[idx].name

#returns a list of all heroes in the game
def getHerolist():
    heroes = request('https://api.opendota.com/api/heroes')
    herolist = []
    for hero in heroes:
        newHero = Hero(hero['localized_name'], hero['id'])
        herolist.append(newHero)
    return herolist

#recommends the top heroes to pick vs an enemy lineup
def suggestHeroPicks(enemyHeroes, herolist, allWinrates):
    for hero in herolist:
        total = 0.0
        winrate = 0.0
        for enemy in enemyHeroes:
            total += allWinrates[hero.ID - 1, enemy.ID - 1]
        winrate = total / len(enemyHeroes)
        hero.winrate = winrate
    herolist.sort(key=lambda x: x.winrate)
    return herolist

def predictWinners(allWinrates, herolist):
    print('Predicting winners...')
    matches = np.loadtxt('matches.csv', delimiter = ',')
    correct = 0.0
    incorrect = 0.0

    for i in range(matches.shape[0]):
        radiant = []
        dire = []        
        if i % 1000 == 0:
            print(i)
        label = matches[i][totalHeroes]
        for j in range(totalHeroes):
            if matches[i][j] == 1.0:
                radiant.append(Hero(getName(j + 1, herolist), j + 1))
            elif matches[i][j] == -1.0:
                dire.append(Hero(getName(j + 1, herolist), j + 1))
        total = 0.0
        for ally in radiant:
            for enemy in dire:
                total += allWinrates[ally.ID - 1, enemy.ID - 1]
        radiantWinChance = total / (len(radiant) * len(dire))
        if radiantWinChance > 0.5 and label == 1:
            correct += 1
        elif radiantWinChance < 0.5 and label == 0:
            correct += 1
        else:
            incorrect += 1
    return correct / (correct + incorrect)

def prediction(radiant, dire, allWinrates):
    total = 0.0
    for ally in radiant:
        for enemy in dire:
            total += allWinrates[ally.ID - 1, enemy.ID - 1]
    return total / (len(radiant) * len(dire))

if __name__ == '__main__':
    herolist = getHerolist()

    #specify allied lineup here
    alliedTeam = ['Omniknight', 'Mirana', 'Pudge', '', '']
    alliedTeam = list(filter(('').__ne__, alliedTeam))
    alliedHeroes = []
    for name in alliedTeam:
        alliedHeroes.append(Hero(name, getID(name, herolist)))

    #specify opposing lineup here
    enemyTeam = ['Outworld Devourer', 'Night Stalker', '', '', '']
    enemyTeam = list(filter(('').__ne__, enemyTeam))
    enemyHeroes = []
    for name in enemyTeam:
        enemyHeroes.append(Hero(name, getID(name, herolist)))

    allWinrates = np.genfromtxt('winrates.csv', delimiter = ',')
    #print('Algorithm accuracy: %f' % predictWinners(allWinrates, herolist))

    pickRankings = suggestHeroPicks(enemyHeroes, herolist, allWinrates)
    for i in range(len(pickRankings)):
        if pickRankings[i].ID not in [o.ID for o in enemyHeroes] and pickRankings[i].ID not in [o.ID for o in alliedHeroes]:
            print(pickRankings[i].name, '-', '{0:.3f}'.format(pickRankings[i].winrate * 100), '%')

    #banRankings = suggestHeroPicks(alliedHeroes, herolist, allWinrates)
    #for i in range(len(banRankings)):
        #if banRankings[i].ID not in [o.ID for o in enemyHeroes] and banRankings[i].ID not in [o.ID for o in alliedHeroes]:
            #print(banRankings[i].name, '-', '{0:3f}'.format(banRankings[i].winrate * 100), '%')           

    print('Consider: carry, support, damage, disables, push, ranged, tank, teamfight')
    pred = prediction(alliedHeroes, enemyHeroes, allWinrates) * 100
    print('{0:.3f}'.format(pred), '% chance to win')