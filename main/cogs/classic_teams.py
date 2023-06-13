import json

import discord
from discord.ext import commands
from main.services.classic_team_functions import *
from main.services.image_functions import ifBuildTeamImageFile, ifBuildSingleTeamImageFile

build_classic_teams()

hex_y = 0xE8E337  # Error message


class ClassicTeamsCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    # TODO: More useful help?
    @commands.command(name="classicTeam", help="Picks one random classic team. Accepts power user input")
    @commands.cooldown(1, 15, commands.BucketType.default)
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
        footer = str(classic_team.player) + " piloted this team to a " + str(classic_team.finish) + " finish from pick " + str(classic_team.pick)

        embed = discord.Embed(title=title)
        embed.set_footer(text=footer)
        embed.set_image(url="attachment://image.png")
        await ctx.send(file=file, embed=embed)

    @commands.command(name="classicTeams", help="Sets up a match of two classic teams")
    @commands.cooldown(1, 15, commands.BucketType.default)
    async def classic_teams(self, ctx):
        classic_teams = []
        classic_team_one: ClassicTeam = get_random_classic_team()
        classic_team_two: ClassicTeam = get_random_classic_team()
        classic_teams.append(classic_team_one.characters)
        classic_teams.append(classic_team_two.characters)

        title = "Two classic teams:"
        file = ifBuildTeamImageFile(classic_teams)
        footer = "Yeah"

        embed = discord.Embed(title=title)
        embed.set_footer(text=footer)
        embed.set_image(url="attachment://image.png")
        await ctx.send(file=file, embed=embed)


async def setup(client):
    await client.add_cog(ClassicTeamsCommands(client))
