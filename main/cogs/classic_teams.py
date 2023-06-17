import json

import discord
from discord.ext import commands
from main.services.classic_team_functions import *
from main.services.image_functions import ifBuildTeamImageFile, ifBuildSingleTeamImageFile
from main.services.random_functions import rfRandomStadium

# Builds the classic teams libraries
build_classic_teams()

NL = "\n"
hex_y = 0xE8E337  # Error message
hex_g = 0xA0AA79

class ClassicTeamsCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="classicTeam", help="Picks one random classic team. Use `!classicTeamHelp` to learn about input")
    @commands.cooldown(1, 20, commands.BucketType.default)
    async def classic_team(self, ctx, *arg):
        if len(arg) == 0:
            classic_team: ClassicTeam = get_random_classic_team()
        else:
            classic_team: ClassicTeam = get_filtered_random_classic_team(arg)
            if not classic_team:
                ctx.command.reset_cooldown(ctx)
                embed = discord.Embed(description="No teams found those parameters", color=hex_y)
                await ctx.send(embed=embed)
                return

        title = "Season " + str(classic_team.season) + " " + str(classic_team.league) + " - " + str(classic_team.player) + "'s Team"
        file = ifBuildSingleTeamImageFile(classic_team.characters)
        footer = classic_team.description()

        embed = discord.Embed(title=title, color=hex_g)
        embed.set_footer(text=footer)
        embed.set_image(url="attachment://image.png")
        await ctx.send(file=file, embed=embed)

    @commands.command(name="classicTeams", help="Sets up a match of two classic teams")
    @commands.cooldown(1, 20, commands.BucketType.default)
    async def classic_teams(self, ctx):
        classic_teams = []
        classic_team_one: ClassicTeam = get_random_classic_team()
        classic_team_two: ClassicTeam = get_random_classic_team()
        classic_teams.append(classic_team_one.characters)
        classic_teams.append(classic_team_two.characters)

        title = "Random Classic Teams"
        file = ifBuildTeamImageFile(classic_teams)
        stadium = rfRandomStadium()
        footer = get_classic_draft_quote()

        embed = discord.Embed(title=title, color=hex_g)
        embed.add_field(name="Stadium", value=stadium)
        embed.set_footer(text=footer)
        embed.set_image(url="attachment://image.png")
        await ctx.send(file=file, embed=embed)

    @commands.command(name="classicTeamHelp", help="Describes \"!classicTeam\" input")
    @commands.cooldown(1, 15, commands.BucketType.default)
    async def classic_team_help(self, ctx):
        title = "Classic Team Help"
        description = "Here are the inputs that the classicTeam command can take:" + NL \
                    + "`<league>` - the name of a league (e.g. galaxy or mario+luigi)" + NL \
                    + "`<player>` - the name of a player" + NL \
                    + "`season=?` - a season number (e.g. season=3)" + NL \
                    + "`pick=?` - the pick number in draft (e.g. pick=2)" + NL \
                    + "`finished=?` - the placement of the team (e.g. finished=1)" + NL \
                    + "All of these can be combined in any order, for example see below: " + NL \
                    + "`!classicTeam mario+luigi pick=2 season=3`" + NL \
                    + "`!classicTeam placed=3 duckydonne`" + NL \
                    + "`!classicTeam result=1 picked=1`"

        embed = discord.Embed(title=title, description=description, color=hex_g)
        await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(ClassicTeamsCommands(client))
