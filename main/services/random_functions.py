from random import shuffle, randint, choice, sample

from helpers.random_team_builder import randomTeamsWithoutDupes, randomTeamsWtihDupes, randomBalancedTeams, \
    randomPowerTeams, randomTeeBallTeams
from resources.characters import Char


# Flip a coin
def rfFlipCoin():
    if randint(0, 1) == 0:
        return "Heads"
    return "Tails"


# Roll a dice with DIE number of sides
def rfRollDice(die):
    if die > 1:
        return randint(1, die)
    return 1


# Pick One from a set of arguments
def rfPickOne(args):
    return choice(args)


# Pick N from a set of arguments. Picks all if N is equal too or greater than the number of arguments
def rfPickMany(choices, args):
    return sample(args, choices)


# Shuffle a set of arguments. We convert to a list because *args is a TUPLE and therefore is immutable
def rfShuffle(args):
    shuffle_list = []
    for arg in args:
        shuffle_list.append(arg)
    shuffle(shuffle_list)
    return shuffle_list


# Picks a random character from all 52 characters in the game
def rfRandomCharacter():
    characters = []
    for char in Char:
        characters.append(char.value)
    shuffle(characters)
    return characters.pop()


# Picks a random stadium
def rfRandomStadium():
    stadiums = ["Mario Stadium", "Peach Garden", "Wario Palace", "Yoshi Park", "DK Jungle", "Bowser Castle"]
    shuffle(stadiums)
    return stadiums.pop()


# Decide on a random mode to play and where
def rfRandomMode():
    random_modes = ["Superstars Off"
                    , "Superstars On"
                    , "BIG BALLA"
                    , "Superstars Off Hazards"
                    , "Remixed"]
    shuffle(random_modes)
    return "Play a game of " + random_modes.pop() + " at " + rfRandomStadium()


# Return two random teams without dupes
def rfRandomTeamsWithoutDupes():
    return randomTeamsWithoutDupes()


# Return two random teams with dupes
def rfRandomTeamsWithDupes():
    return randomTeamsWtihDupes()


# Return two balanced teams
def rfRandomBalancedTeams():
    return randomBalancedTeams()


# Return two power teams
def rfRandomPowerTeams():
    return randomPowerTeams()


def rfRandomTeeBallTeams():
    return randomTeeBallTeams()
