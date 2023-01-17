import copy
from random import shuffle, choice
from resources.characters import Char

# General Character Lists
all_captains = [Char.MARIO, Char.LUIGI, Char.PEACH, Char.DAISY, Char.YOSHI, Char.BIRDO, Char.DIDDY, Char.DK, Char.WALUIGI, Char.WARIO, Char.BOWSER_JR, Char.BOWSER]
bro_list = [Char.BRO_H, Char.BRO_B, Char.BRO_F]
mag_list = [Char.MAGIKOOPA_B, Char.MAGIKOOPA_G, Char.MAGIKOOPA_Y, Char.MAGIKOOPA_R]
pianta_list = [Char.PIANTA_R, Char.PIANTA_B, Char.PIANTA_Y]
noki_list = [Char.NOKI_R, Char.NOKI_B, Char.NOKI_G]
paratroopa_list = [Char.PARATROOPA_G, Char.PARATROOPA_R]
koopa_list = [Char.KOOPA_R, Char.KOOPA_G]
shyguy_list = [Char.SHY_GUY_R, Char.SHY_GUY_B, Char.SHY_GUY_G, Char.SHY_GUY_Y, Char.SHY_GUY_BK]
drybones_list = [Char.DRY_BONES_G, Char.DRY_BONES_R, Char.DRY_BONES_B, Char.DRY_BONES_GY]
toad_list = [Char.TOAD_R, Char.TOAD_B, Char.TOAD_G, Char.TOAD_P, Char.TOAD_Y]

# 32 Character Random, Random Variant
pnd_characters = [Char.BOWSER, Char.PETEY, Char.DK, bro_list, Char.YOSHI, Char.BIRDO, Char.BOO, Char.KING_BOO, mag_list, Char.WALUIGI, Char.WARIO, Char.TOADSWORTH, pianta_list, Char.MARIO, Char.LUIGI,
                  Char.DIDDY, Char.DIXIE, noki_list, paratroopa_list, Char.DAISY, Char.TOADETTE, Char.BOWSER_JR, shyguy_list, drybones_list, Char.PEACH, koopa_list, toad_list, Char.MONTY,
                  Char.BABY_MARIO, Char.BABY_LUIGI, Char.GOOMBA, Char.PARAGOOMBA]


def pickFromPool(team, pool):
    next_pick = pool.pop()
    if isinstance(next_pick, list):
        team.append(choice(next_pick))
    else:
        team.append(next_pick)
# END pickfromPool


def pickFromSpecializedPool(team, specialized_pool, pool):
    shuffle(specialized_pool)
    team.append(specialized_pool.pop())
    pool.remove(team[-1])
# END pickFromSpecializedPool


def pureRandomTeams(team_one, team_two, pool, captains, pitchers=None):

    shuffle(captains)
    pickFromSpecializedPool(team_one, captains, pool)
    pickFromSpecializedPool(team_two, captains, pool)

    if pitchers:
        if team_one[0] in pitchers and team_two[0] not in pitchers:
            pitchers.remove(team_one[0])
            pickFromSpecializedPool(team_two, pitchers, pool)
        elif team_two[0] in pitchers and team_one[0] not in pitchers:
            pitchers.remove(team_two[0])
            pickFromSpecializedPool(team_one, pitchers, pool)
        elif team_one[0] not in pitchers and team_two[0] not in pitchers:
            pickFromSpecializedPool(team_two, pitchers, pool)
            pickFromSpecializedPool(team_one, pitchers, pool)

        if len(team_one) > len(team_two):
            pickFromPool(team_two, pool)
        elif len(team_two) > len(team_one):
            pickFromPool(team_one, pool)

    shuffle(pool)
    while len(team_one) + len(team_two) < 18:
        pickFromPool(team_one, pool)
        pickFromPool(team_two, pool)
# END pureRandomTeams


def randomTeamsWithoutDupes():
    first_team = []
    second_team = []
    pureRandomTeams(first_team, second_team, copy.deepcopy(pnd_characters), copy.deepcopy(all_captains))
    return [first_team, second_team]
# END randomTeamsWithoutDupes


def randomTeamsWtihDupes():
    first_team = []
    second_team = []
    all_characters = []
    for char in Char:
        all_characters.append(char)
    shuffle(all_characters)
    pureRandomTeams(first_team, second_team, all_characters, copy.deepcopy(all_captains))
    return [first_team, second_team]
# END randomTeamsWithDupes


# Broad Balanced Tiers
tier_0 = [Char.BOWSER, Char.PETEY, Char.DK, Char.BRO_H, Char.BRO_B, Char.BRO_F, Char.YOSHI, Char.BIRDO, Char.BOO, Char.KING_BOO]
tier_1 = [Char.MAGIKOOPA_B, Char.MAGIKOOPA_R, Char.MAGIKOOPA_G, Char.MAGIKOOPA_Y, Char.WALUIGI, Char.TOADSWORTH, Char.MARIO,
          Char.WARIO, Char.PIANTA_R, Char.LUIGI, Char.DIDDY, Char.DIXIE]
tier_2 = [Char.NOKI_G, Char.PARATROOPA_G, Char.TOADETTE, Char.BOWSER_JR, Char.DRY_BONES_G, Char.DAISY, Char.PIANTA_Y, Char.PIANTA_B,
          Char.NOKI_B, Char.NOKI_R, Char.PEACH, Char.SHY_GUY_R]
tier_3 = [Char.DRY_BONES_R, Char.SHY_GUY_G, Char.TOAD_R, Char.SHY_GUY_BK, Char.SHY_GUY_B, Char.SHY_GUY_Y, Char.KOOPA_G,
          Char.MONTY, Char.PARATROOPA_R, Char.KOOPA_R]
tier_4 = [Char.DRY_BONES_GY, Char.DRY_BONES_B, Char.TOAD_B, Char.TOAD_G, Char.TOAD_P, Char.TOAD_Y, Char.BABY_MARIO, Char.BABY_LUIGI,
          Char.GOOMBA, Char.PARAGOOMBA]

balanced_brackets = [tier_0.copy(), tier_1.copy(), tier_2.copy(), tier_3.copy(), tier_4.copy()]
balanced_captains = {Char.BOWSER: 0, Char.DK: 0, Char.YOSHI: 0, Char.BIRDO: 0, Char.WALUIGI: 1, Char.WARIO: 1, Char.MARIO: 1,
                     Char.LUIGI: 1, Char.DIDDY: 1, Char.DAISY: 2, Char.BOWSER_JR: 2, Char.PEACH: 2}


def pickFromBrackets(team_one, team_two, brackets):
    shuffle(brackets)
    tier = brackets.pop()
    if len(tier) > 1:
        shuffle(tier)
        team_one.append(tier.pop())
        team_two.append(tier.pop())
        if len(tier) > 1:
            brackets.append(tier)
# END pickFromBrackets


def pickBalancedCaptains(team_one, team_two, captain_dict, brackets):
    # Assign captains
    captain_list = list(captain_dict.keys())
    shuffle(captain_list)
    team_one.append(captain_list[0])
    team_two.append(captain_list[1])

    team_one_cap_tier = captain_dict[team_one[0]]
    team_two_cap_tier = captain_dict[team_two[0]]
    brackets[team_one_cap_tier].remove(team_one[0])
    brackets[team_two_cap_tier].remove(team_two[0])

    # Balance Teams
    if team_one_cap_tier == team_two_cap_tier:
        return

    team_two.append(brackets[team_one_cap_tier].pop())
    team_one.append(brackets[team_two_cap_tier].pop())
# END pickBalancedCaptains


def pickBalancedTeams(team_one, team_two, brackets, captain_dict):
    pickBalancedCaptains(team_one, team_two, captain_dict, brackets)

    while len(team_one) + len(team_two) < 18:
        pickFromBrackets(team_one, team_two, brackets)
# End pickBalancedTeams


def randomBalancedTeams():
    first_team = []
    second_team = []
    pickBalancedTeams(first_team, second_team, copy.deepcopy(balanced_brackets), copy.deepcopy(balanced_captains))

    return [first_team, second_team]
# END randomBalancedTeams


# Power Team Definitions
power_characters = [Char.BOWSER, Char.DK, Char.PETEY, Char.BIRDO, Char.BOO, Char.BRO_H, Char.YOSHI, Char.KING_BOO, Char.BRO_B,
                    Char.BRO_F, Char.MAGIKOOPA_B, Char.MAGIKOOPA_R, Char.MAGIKOOPA_G, Char.MAGIKOOPA_Y, Char.WALUIGI, Char.WARIO, Char.MARIO,
                    Char.LUIGI, Char.PIANTA_R, Char.DIXIE, Char.DIDDY, Char.TOADSWORTH, Char.NOKI_G, Char.PARATROOPA_G]
power_captains = [Char.BOWSER, Char.DK, Char.BIRDO, Char.YOSHI, Char.WALUIGI, Char.WARIO, Char.MARIO, Char.LUIGI, Char.DIDDY]
power_pitchers = [Char.BOO, Char.DIXIE, Char.DIDDY, Char.WALUIGI]


def randomPowerTeams():
    first_team = []
    second_team = []
    pureRandomTeams(first_team, second_team, copy.deepcopy(power_characters), copy.deepcopy(power_captains), copy.deepcopy(power_pitchers))
    return [first_team, second_team]
# END randomPowerTeams


# Tee Ball Team Definitions
teeball_characters = [Char.MARIO, Char.LUIGI, Char.WALUIGI, Char.WARIO, Char.TOADSWORTH, Char.PIANTA_R, Char.NOKI_G, Char.PARATROOPA_G,
                      Char.PEACH, Char.DAISY, Char.PIANTA_Y, Char.PIANTA_B, Char.DRY_BONES_G, Char.DRY_BONES_GY, Char.TOADETTE,
                      Char.TOAD_R, Char.SHY_GUY_BK, Char.SHY_GUY_R, Char.NOKI_B, Char.NOKI_R, Char.TOAD_P, Char.BOWSER_JR,
                      Char.KOOPA_R, Char.TOAD_B, Char.TOAD_G, Char.TOAD_Y, Char.SHY_GUY_B, Char.SHY_GUY_G, Char.SHY_GUY_Y,
                      Char.PARAGOOMBA, Char.GOOMBA, Char.BABY_MARIO, Char.BABY_LUIGI, Char.DRY_BONES_B, Char.DRY_BONES_R,
                      Char.MONTY, Char.KOOPA_G, Char.PARATROOPA_R]
teeball_captains = [Char.MARIO, Char.LUIGI, Char.WALUIGI, Char.WARIO, Char.PEACH, Char.DAISY, Char.BOWSER_JR]


def randomTeeBallTeams():
    first_team = []
    second_team = []
    pureRandomTeams(first_team, second_team, copy.deepcopy(teeball_characters), copy.deepcopy(teeball_captains))
    return [first_team, second_team]
