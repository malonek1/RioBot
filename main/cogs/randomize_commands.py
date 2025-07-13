import discord
from discord.ext import commands

from services.image_functions import ifBuildTeamImageFile
from services.random_functions import *

# Random Cog Properties
hex_y = 0xE8E337  # Error message
hex_r = 0xF46D75  # Success message

NL = "\n"
random_help_string = "Here is a list of random commands you can use and their functions:" + NL \
                     + "`!random teams` - Generate two random teams with no dupes but random variants" + NL \
                     + "`!random teams dupes` - Generate two random teams with dupes enabled" + NL \
                     + "`!random teams balanced` - Generate two broadly balanced teams" + NL \
                     + "`!random teams teeball` - Generate two tee-ball teams using the tee-ball roster" + NL \
                     + "`!random teams power` - Generate two teams with top tier characters and distributed pitching" + NL \
                     + "`!random stadium` - Returns a random stadium" + NL \
                     + "`!random character` - Returns a random character" + NL \
                     + "`!random mode` - Returns a random game type for you to play" + NL \
                     + "`!pick options...` - Picks an option randomly" + NL \
                     + "`!pickmany N options...` - Picks N options randomly" + NL \
                     + "`!shuffle options...` - Shuffles options and returns them" + NL \
                     + "`!coin` or `!flip` - Flip a coin" + NL \
                     + "`!roll N` - Roll a die of N sides"


# Cog Class
class RandomizeCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="random", help="Random Baseball Functions. Please use `!random help` for more info")
    @commands.cooldown(1, 10, commands.BucketType.default)
    async def random(self, ctx, command, qualifier=""):
        command = command.lower()
        qualifier = qualifier.lower()
        if "help" in command:
            ctx.command.reset_cooldown(ctx)
            embed = discord.Embed(title="Random Commands Help", description=random_help_string)
            await ctx.send(embed=embed)
        elif command == "character" or command == "chara" or command == "char":
            if not qualifier or qualifier == "":
                embed = discord.Embed(title=rfRandomCharacter(), color=hex_r)
            else:
                try:
                    embed = discord.Embed(description=rfRandomCharacters(int(qualifier)), color=hex_r)
                except ValueError:
                    embed = discord.Embed(title=rfRandomCharacter(), color=hex_r)
            await ctx.send(embed=embed)
        elif command == "stadium":
            embed = discord.Embed(title=rfRandomStadium(), color=hex_r)
            await ctx.send(embed=embed)
        elif command == "mode" or command == "modes":
            embed = discord.Embed(title=rfRandomMode(), color=hex_r)
            await ctx.send(embed=embed)
        elif command == "teams":
            if not qualifier or qualifier == "":
                team_list = rfRandomTeamsWithoutDupes()
                title = "**Random Teams**"
                description = "Pure random teams without dupes but random variants. Captains are highlighted."
            elif "dupes" in qualifier:
                team_list = rfRandomTeamsWithDupes()
                title = "**Random Teams with Dupes** "
                description = "Pure random teams with duplicates enabled. Captains are highlighted."
            elif "balance" in qualifier:
                team_list = rfRandomBalancedTeams()
                title = "**Random Balanced Teams**"
                description = "Random teams where each team is given a character from one of five broadly balanced " \
                              "tiers until teams are filled. Captains are highlighted."
            elif "power" in qualifier:
                team_list = rfRandomPowerTeams()
                title = "**Random Power Teams**"
                description = "Random teams made from top characters exclusively. Duplicates are enabled. Each team " \
                              "is guaranteed one meta pitcher. Captains are highlighted."
            elif "teeball" in qualifier:
                team_list = rfRandomTeeBallTeams()
                title = "**Random Tee-Ball Teams**"
                description = "Random teams made from the Tee-Ball roster. This excludes the top 9 characters " \
                              "as well as diddy & dixie."

            captain_list = [team_list[0][0], team_list[1][0]]

            file = ifBuildTeamImageFile(team_list, captain_list)
            embed = discord.Embed(title=title, description=description, color=hex_r)
            embed.set_image(url="attachment://image.png")
            await ctx.send(file=file, embed=embed)

        else:
            ctx.command.reset_cooldown(ctx)
            embed = discord.Embed(description="Alas poor random command; I do not know thee well", color=hex_y)
            await ctx.send(embed=embed)

    # End random

    @commands.command(name="pick", help="Pick one item from a list")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pick(self, ctx, *arg):
        if len(arg) > 1:
            embed = discord.Embed(description=rfPickOne(arg), color=hex_r)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description="Please give me more options than that", color=hex_y)
            await ctx.send(embed=embed)

    # End pick

    @commands.command(name="pickmany", help="Pick N items from a list")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pick_many(self, ctx, choices, *arg):
        try:
            pick_number = int(choices)
            if len(arg) > 0 and pick_number < len(arg):
                embed = discord.Embed(description=rfPickMany(pick_number, arg), color=hex_r)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(description="I don't think you quite know what you're asking", color=hex_y)
                await ctx.send(embed=embed)
        except ValueError:
            embed = discord.Embed(description="Give me a number of choices to make. For example: `!pickmany 2 red "
                                              "blue green`", color=hex_y)
            await ctx.send(embed=embed)

    # End pick many

    @commands.command(name="shuffle", help="Shuffle the order of a list")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def shuffle(self, ctx, *arg):
        if len(arg) > 1:
            embed = discord.Embed(description=rfShuffle(arg), color=hex_r)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description="No sense in shuffling that", color=hex_y)
            await ctx.send(embed=embed)

    # End shuffle

    @commands.command(name="coin", aliases=["flip", "flipcoin"], help="coin, flip, flipcoin")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def coin(self, ctx):
        embed = discord.Embed(title=rfFlipCoin(), color=hex_r)
        await ctx.send(embed=embed)

    # End coin

    @commands.command(name="roll", help="Roll an N-sided die")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def roll(self, ctx, die):
        try:
            die_sides = int(die)
            if die_sides > 2:
                embed = discord.Embed(title=rfRollDice(die_sides), color=hex_r)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(description="I can't roll that in this dimension", color=hex_y)
                await ctx.send(embed=embed)
        except ValueError:
            embed = discord.Embed(description="That isn't a dice", color=hex_y)
            await ctx.send(embed=embed)
    # End roll


async def setup(client):
    await client.add_cog(RandomizeCommands(client))
