from io import BytesIO

import discord
import requests
from PIL import Image, ImageOps
from resources.characters import images

image_width = 52
image_height = 60
border_offset = 4

def build_team_image(team):
    team_icons = []
    for character in team:
        team_icons.append(load_image_for_character(character.value))

    total_width = 9*image_width
    total_height = 1*image_height
    team_image = Image.new('RGBA', (total_width, total_height))
    x_offset = 0
    for icon in team_icons:
        team_image.paste(icon, (x_offset, 0))
        x_offset += image_width

    return team_image
# END build_team_image


# Builds a composite image showing two team rosters displayed horizontally
def build_teams_image(teams):
    team_one_icons = []
    team_two_icons = []
    for character in teams[0]:
        team_one_icons.append(load_image_for_character(character.value))
    for character in teams[1]:
        team_two_icons.append(load_image_for_character(character.value))

    total_width = 9*image_width
    total_height = 2*image_height

    teams_image = Image.new('RGBA', (total_width, total_height))
    x_offset = 0
    for icon in team_one_icons:
        teams_image.paste(icon, (x_offset, 0))
        x_offset += image_width
    x_offset = 0
    for icon in team_two_icons:
        teams_image.paste(icon, (x_offset, image_height))
        x_offset += image_width

    return teams_image
# END buildTeamImage


# Builds a composite image showing two team rosters displayed horizontally with the Captains highlighted cyan
def build_teams_image_highlight_captain(teams, captains):
    team_one_icons = []
    team_two_icons = []
    for character in teams[0]:
        image = load_image_for_character(character.value)
        if character in captains:
            background = Image.new('RGBA', (image_width-border_offset, image_height-border_offset))
            bordered = ImageOps.expand(background, 2, (0, 255, 255))
            bordered.paste(image, (0, 0), image)
            image = bordered
        team_one_icons.append(image)
    for character in teams[1]:
        image = load_image_for_character(character.value)
        if character in captains:
            background = Image.new('RGBA', (image_width-border_offset, image_height-border_offset))
            bordered = ImageOps.expand(background, 2, (0, 255, 255))
            bordered.paste(image, (0, 0), image)
            image = bordered
        team_two_icons.append(image)

    total_width = 9*image_width
    total_height = 2*image_height

    teams_image = Image.new('RGBA', (total_width, total_height))
    x_offset = 0
    for icon in team_one_icons:
        teams_image.paste(icon, (x_offset, 0))
        x_offset += image_width
    x_offset = 0
    for icon in team_two_icons:
        teams_image.paste(icon, (x_offset, image_height))
        x_offset += image_width

    return teams_image
# END buildTeamImage


def convert_image_to_file(team_image):
    with BytesIO() as image_binary:
        team_image.save(image_binary, 'PNG')
        image_binary.seek(0)
        file = discord.File(fp=image_binary, filename='image.png')
        return file
# End convertImageToFile


def load_image_for_character(character_name):
    path = "./images/" + character_name + ".png"
    return Image.open(path).convert('RGBA')
# End loadImageForCharacter
