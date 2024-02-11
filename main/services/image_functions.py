from helpers.image_builder import *
from helpers.team_sorter import sort_teams_by_tier, sort_team_by_tier


def ifBuildTeamImageFile(teams, captains=None, sort=True):
    if sort:
        teams = sort_teams_by_tier(teams)

    if captains:
        teams_image = build_teams_image_highlight_captain(teams, captains)
    else:
        teams_image = build_teams_image(teams)

    return convert_image_to_file(teams_image)
# END ifBuildTeamImageFile


def ifBuildSingleTeamImageFile(team, sort=False):
    if sort:
        team = sort_team_by_tier(team)
    team_image = build_team_image(team)

    return convert_image_to_file(team_image)