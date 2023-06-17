from random import choice, shuffle
from main.helpers.classic_teams_parser import *

season_aliases = ["season"]
pick_aliases = ["pick", "picked", "select", "selection"]
finish_aliases = ["finish", "finished", "placement", "placed", "result"]


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


def get_classic_draft_quote():
    quotes = ["I wonder when we will get dinger city classic teams added to this - girl who coded this"
              , "Bababooey! You have been visited by the ghost of grump classic."
              , "played a classic with mori and he had ball dash petey it was the scariest thing ever - faceman"
              , "classic canada - Pokebunny"
              , "Classic dad shoe - Buffcat"
              , "classic just appeals to a wider audience outside of baseball - VicklessFalcon"
              , "Genshin is a classic \"game is fine but the fanbase got a lot of weirdos\" game - Joon"
              , "Classic best format - MORI"
              , "Classic format is very fun - PeacockSlayer"
              , "Glad I could be here guys, can't wait to see who'll get 2nd! - guy who came in 2nd"
              , "I was bringing back a classic joke - DaJoeMyster"
              , "i love the world baseball classic - Cammie"
              , "Classic is so cool - duckydonne"
              , "Classic 51 hit game - BMills"
    ]
    return choice(quotes)
