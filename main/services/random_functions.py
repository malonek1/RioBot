from random import randint, choice, sample, shuffle

from resources.characters import Char

# Misc randomization helpers. Team construction lives in
# helpers/random_team_builder.py; this module covers everything else.

STADIUMS = ["Mario Stadium", "Peach Garden", "Wario Palace", "Yoshi Park", "DK Jungle", "Bowser Castle"]
# Hazards mode avoids Mario Stadium (its hazards aren't wanted).
HAZARDS_STADIUMS = [s for s in STADIUMS if s != "Mario Stadium"]

RANDOM_MODES = ["Superstars Off", "Superstars On", "BIG BALLA", "Superstars Off Hazards", "Remixed", "Quickplay"]
QUICKPLAY_MODES = ["Superstars Off Hazards", "Superstars On", "Big Balla"]


# Flip a coin
def rfFlipCoin():
    return "Heads" if randint(0, 1) == 0 else "Tails"


# Roll a die with DIE number of sides
def rfRollDice(die):
    return randint(1, die) if die > 1 else 1


# Pick one from a set of arguments
def rfPickOne(args):
    return choice(args)


# Pick N from a set of arguments. Picks all if N >= the number of arguments
def rfPickMany(choices, args):
    return sample(args, choices)


# Shuffle a set of arguments into a new list (args may be an immutable tuple)
def rfShuffle(args):
    shuffle_list = list(args)
    shuffle(shuffle_list)
    return shuffle_list


# Picks a random character from all characters in the game
def rfRandomCharacter():
    return choice([char.value for char in Char])


# Picks NUM random characters (with replacement), clamped to 1-9
def rfRandomCharacters(num, preserve_enum=False):
    num = max(1, min(num, 9))
    characters = list(Char) if preserve_enum else [char.value for char in Char]
    return [choice(characters) for _ in range(num)]


def rfRandomCharactersG():
    character_list = list(Char)
    team = [character_list[10], character_list[11], character_list[2], character_list[53], character_list[10],
            character_list[17], character_list[34], character_list[10], character_list[11]]
    shuffle(team)
    return team


# Picks a random stadium
def rfRandomStadium():
    return choice(STADIUMS)


def rfRandomHazardsStadium():
    return choice(HAZARDS_STADIUMS)


# Decide on a random mode to play
def rfRandomMode():
    return choice(RANDOM_MODES)


def rfRandomQuickplayMode():
    return choice(QUICKPLAY_MODES)
