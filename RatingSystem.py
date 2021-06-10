# THIS SCRIPT IS NOT PART OF THE GAME, IT IS MEANT TO TEST NUMBERS FOR THE RATING SYSTEM

import random
import math

START_RATING = 600
RATING_STEP = 100
MAX_STEP = 50000000000
LOSER_MULT = 0.5


class Player:
    def __init__(self, ID, skill):
        self.ID = ID

        self.skill = skill
        self.rating = START_RATING


players = [Player(i, random.randint(10, 100)) for i in range(9)]

matches = []

for i in range(len(players)):
    for j in range(i+1, len(players)):
        matches.append((players[i], players[j]))

random.shuffle(matches)
for match in matches:
    if random.randint(1, sum([ply.skill for ply in match])) <= match[0].skill:
        winner = match[0]
        loser = match[1]
    else:
        winner = match[1]
        loser = match[0]

    CHANGE = min(abs(loser.rating / winner.rating) * RATING_STEP, MAX_STEP)

    print("Match between", list([str(p.ID) + "("+str(p.skill)+")" for p in match]), "concluded")
    print("WINNER:", str(winner.ID) + "("+str(winner.skill)+")", "RATING:", winner.rating, "+", CHANGE, "=", winner.rating + CHANGE)
    print("LOSER:", str(loser.ID) + "("+str(loser.skill)+")", "RATING:", loser.rating, "-", CHANGE*LOSER_MULT, "=", loser.rating - CHANGE*LOSER_MULT)
    print()

    winner.rating += CHANGE
    loser.rating -= CHANGE * LOSER_MULT

for p in players:
    print("ID:", p.ID, "Skill:", p.skill, "Rating:", p.rating)
