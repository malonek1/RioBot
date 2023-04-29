from io import BytesIO

import discord
import requests
from PIL import Image, ImageOps
from resources.characters import images


# Builds a composite image showing two team rosters displayed horizontally
def buildTeamImage(teams):
    team_one_icons = []
    team_two_icons = []
    for character in teams[0]:
        team_one_icons.append(Image.open(requests.get(images[character.value], stream=True).raw))
    for character in teams[1]:
        team_two_icons.append(Image.open(requests.get(images[character.value], stream=True).raw))

    total_width = 9*60
    total_height = 2*60

    teams_image = Image.new('RGBA', (total_width, total_height))
    x_offset = 0
    for icon in team_one_icons:
        teams_image.paste(icon, (x_offset, 0))
        x_offset += 60
    x_offset = 0
    for icon in team_two_icons:
        teams_image.paste(icon, (x_offset, 60))
        x_offset += 60

    return teams_image
# END buildTeamImage


# Builds a composite image showing two team rosters displayed horizontally with the Captains highlighted cyan
def buildTeamImageHighlightCaptain(teams, captains):
    team_one_icons = []
    team_two_icons = []
    for character in teams[0]:
        image = Image.open(requests.get(images[character.value], stream=True).raw).convert('RGBA')
        if character in captains:
            background = Image.new('RGBA', (56, 56))
            bordered = ImageOps.expand(background, 2, (0, 255, 255))
            bordered.paste(image, (0, 0), image)
            image = bordered
        team_one_icons.append(image)
    for character in teams[1]:
        image = Image.open(requests.get(images[character.value], stream=True).raw).convert('RGBA')
        if character in captains:
            background = Image.new('RGBA', (56, 56))
            bordered = ImageOps.expand(background, 2, (0, 255, 255))
            bordered.paste(image, (0, 0), image)
            image = bordered
        team_two_icons.append(image)

    total_width = 9*60
    total_height = 2*60

    teams_image = Image.new('RGBA', (total_width, total_height))
    x_offset = 0
    for icon in team_one_icons:
        teams_image.paste(icon, (x_offset, 0))
        x_offset += 60
    x_offset = 0
    for icon in team_two_icons:
        teams_image.paste(icon, (x_offset, 60))
        x_offset += 60

    return teams_image
# END buildTeamImage


def convertImageToFile(team_image):
    with BytesIO() as image_binary:
        team_image.save(image_binary, 'PNG')
        image_binary.seek(0)
        file = discord.File(fp=image_binary, filename='image.png')
        return file
# End convertImageToFile
