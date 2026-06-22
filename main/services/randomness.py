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
def flip_coin():
    return "Heads" if randint(0, 1) == 0 else "Tails"


# Roll a die with DIE number of sides
def roll_dice(die):
    return randint(1, die) if die > 1 else 1


# Pick one from a set of arguments
def pick_one(args):
    return choice(args)


# Pick N from a set of arguments. Picks all if N >= the number of arguments
def pick_many(choices, args):
    return sample(args, choices)


# Shuffle a set of arguments into a new list (args may be an immutable tuple)
def shuffle_list(args):
    shuffle_list = list(args)
    shuffle(shuffle_list)
    return shuffle_list


# Picks a random character from all characters in the game
def random_character():
    return choice([char.value for char in Char])


# Picks NUM random characters (with replacement), clamped to 1-9
def random_characters(num, preserve_enum=False):
    num = max(1, min(num, 9))
    characters = list(Char) if preserve_enum else [char.value for char in Char]
    return [choice(characters) for _ in range(num)]


def random_characters_g():
    character_list = list(Char)
    team = [character_list[10], character_list[11], character_list[2], character_list[53], character_list[10],
            character_list[17], character_list[34], character_list[10], character_list[11]]
    shuffle(team)
    return team


# Picks a random stadium
def random_stadium():
    return choice(STADIUMS)


def random_hazards_stadium():
    return choice(HAZARDS_STADIUMS)


# Decide on a random mode to play
def random_mode():
    return choice(RANDOM_MODES)


def random_quickplay_mode():
    return choice(QUICKPLAY_MODES)
