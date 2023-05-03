from helpers.image_builder import *
from helpers.team_sorter import sortTeamsByTier


def ifBuildTeamImageFile(teams, captains=None, sort=True):
    if sort:
        teams = sortTeamsByTier(teams)

    if captains:
        teams_image = buildTeamImageHighlightCaptain(teams, captains)
    else:
        teams_image = buildTeamImage(teams)

    return convertImageToFile(teams_image)
# END ifBuildTeamImageFile
