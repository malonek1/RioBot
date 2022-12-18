from resources.characters import Char

ranked_character_dict = {
    Char.BOWSER.value: 1,
    Char.PETEY.value: 2,
    Char.DK.value: 3,
    Char.BRO_H.value: 4,
    Char.BRO_B.value: 4,
    Char.YOSHI.value: 5,
    Char.BIRDO.value: 6,
    Char.BOO.value: 7,
    Char.KING_BOO.value: 8,
    Char.BRO_F.value: 9,
    Char.MAGIKOOPA_B.value: 10,
    Char.MAGIKOOPA_R.value: 10,
    Char.MAGIKOOPA_G.value: 10,
    Char.MAGIKOOPA_Y.value: 10,
    Char.WALUIGI.value: 11,
    Char.TOADSWORTH.value: 12,
    Char.MARIO.value: 13,
    Char.WARIO.value: 14,
    Char.PIANTA_R.value: 15,
    Char.LUIGI.value: 16,
    Char.DIDDY.value: 17,
    Char.DIXIE.value: 17,
    Char.NOKI_G.value: 18,
    Char.PARATROOPA_G.value: 19,
    Char.TOADETTE.value: 20,
    Char.BOWSER_JR.value: 21,
    Char.DRY_BONES_G.value: 22,
    Char.DAISY.value: 23,
    Char.PIANTA_B.value: 24,
    Char.PIANTA_Y.value: 24,
    Char.NOKI_B.value: 25,
    Char.NOKI_R.value: 25,
    Char.PEACH.value: 26,
    Char.SHY_GUY_R.value: 27,
    Char.SHY_GUY_G.value: 27,
    Char.DRY_BONES_R.value: 28,
    Char.TOAD_R.value: 29,
    Char.SHY_GUY_B.value: 30,
    Char.SHY_GUY_Y.value: 30,
    Char.SHY_GUY_BK.value: 30,
    Char.KOOPA_G.value: 31,
    Char.MONTY.value: 32,
    Char.PARATROOPA_R.value: 33,
    Char.KOOPA_R.value: 34,
    Char.DRY_BONES_B.value: 35,
    Char.DRY_BONES_GY.value: 35,
    Char.TOAD_B.value: 36,
    Char.TOAD_P.value: 36,
    Char.TOAD_G.value: 36,
    Char.TOAD_Y.value: 36,
    Char.BABY_MARIO.value: 37,
    Char.BABY_LUIGI.value: 37,
    Char.GOOMBA.value: 38,
    Char.PARAGOOMBA.value: 38
}


def getCharacterRank(char):
    if isinstance(char, Char):
        return ranked_character_dict[char.value]
    else:
        if char in ranked_character_dict:
            return ranked_character_dict[char]
        else:
            return 99   # Put any unknown characters at end of list
# END getCharacterRank


def sortTeamsByTier(teams):
    for team in teams:
        team.sort(key=getCharacterRank)
    return teams
# END Sort Teams By Tier Exclude Captain


def sortTeamsByTierExcludeCaptain(teams):
    for team in teams:
        captain = team.pop(0)
        team.sort(key=getCharacterRank)
        team.insert(0, captain)
    return teams
# END Sort Teams By Tier Exclude Captain
