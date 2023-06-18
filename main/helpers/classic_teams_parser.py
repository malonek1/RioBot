import csv
from random import shuffle
from main.helpers.utils import ordinal
from main.resources.characters import Char

# Static variables of which row in the CSV are which
league_row = 0
season_row = 1
pick_row = 2
finish_row = 3
player_row = 4
char_row_start = 5
char_row_end = 13

classic_teams_collection = []
classic_team_leagues = []
classic_team_players = []


class ClassicTeam:
    def __init__(self):
        pass

    def __init__(self, league, player, characters, season, pick, finish):
        self.league = league
        self.player = player
        self.characters = characters
        self.pick = pick
        self.season = season
        self.finish = finish

    def description(self):
        pick = self.pick
        if "Auction" not in pick:
            pick = ordinal(self.pick)
        descriptions = [
            str(self.player) + " piloted this team to a " + ordinal(self.finish) + " finish from " + pick + " pick.",
            "This " + ordinal(self.finish) + " place team was managed by " + str(self.player) + " with " + pick + " pick in the draft.",
            "Led by " + str(self.player) + ", this " + pick + " pick team finished " + ordinal(self.finish) + " in the league.",
            "With " + pick + " selection in the draft, this team made it to " + ordinal(self.finish) + " place thanks to coaching from " + str(self.player) + ".",
            "Coming " + ordinal(self.finish) + " in the league was possible thanks to daft handling of " + pick + " pick by " + str(self.player) + "."
        ]
        shuffle(descriptions)
        return descriptions.pop()


def build_character_list(char_row):
    characters = []
    i = char_row_start
    while i <= char_row_end:
        characters.append(Char(char_row[i]))
        i += 1
    return characters


def build_classic_teams():
    with open('resources/ClassicTeams.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            classic_team_leagues.append(row[league_row].lower())
            classic_team_players.append(row[player_row].lower())
            classic_teams_collection.append(ClassicTeam(row[league_row],
                                                        row[player_row],
                                                        build_character_list(row),
                                                        row[season_row],
                                                        row[pick_row],
                                                        row[finish_row]))


def get_classic_teams():
    return classic_teams_collection


def get_classic_team_leagues():
    return classic_team_leagues


def get_classic_team_players():
    return classic_team_players
