# from helpers.classic_teams_parser import *
from random import choice

from main.helpers.classic_teams_parser import *

season_aliases = ["season"]
pick_aliases = ["pick", "select", "selection"]
finish_aliases = ["finish", "finished", "placement", "placed"]


def get_random_classic_team():
    return choice(get_classic_teams())


def get_filtered_random_classic_team(args):
    return choice(find_classic_teams(args))


def matches_team_filter(filter_team: ClassicTeam, potential_team: ClassicTeam):
    if filter_team.league and potential_team.league.lower() != filter_team.league:
        return False
    elif filter_team.player and potential_team.player.lower() != filter_team.player:
        return False
    elif filter_team.season and potential_team.season != filter_team.season:
        return False
    elif filter_team.pick and potential_team.pick != filter_team.pick:
        return False
    elif filter_team.finish and potential_team.finish != filter_team.finish:
        return False
    else:
        return True


def find_classic_teams(args):
    team_filter = ClassicTeam(None, None, None, None, None, None)
    for option in args:
        option = option.lower()
        if option in get_classic_team_players():
            team_filter.player = option
        elif option in get_classic_team_leagues():
            team_filter.league = option
        elif "=" in option:
            option = option.split('=')
            if option[0] in season_aliases:
                team_filter.season = option[1]
            elif option[0] in pick_aliases:
                team_filter.pick = option[1]
            elif option[0] in finish_aliases:
                team_filter.finish = option[1]

    classic_teams = get_classic_teams()
    try:
        return [classic_team for classic_team in classic_teams if matches_team_filter(team_filter, classic_team)]
    except IndexError:
        print("Index Error occurred")
        return None
