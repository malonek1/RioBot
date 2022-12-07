import discord
from discord.ext import commands

from resources import CharacterStats

stats_lol = []
CharacterStats.build_stats_lol(stats_lol)
CharacterStats.build_stat_objs()


class GameStatLookup(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Stats command
    # Character is either the character who's stat you want or "highest", "lowest", "average"
    # Stat is the stat you want to grab
    @commands.command(name="stat", help="Look up in-game character stats")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def stat(self, ctx, character: str, stat: str):
        character = character.lower()  # ignore case-sensitivity stuff
        stat = stat.lower()  # ignore case-sensitivity stuff
        arg1 = CharacterStats.find_character(character)  # returns row index of character
        arg2 = CharacterStats.find_stat(stat)  # returns column index of character

        # check for invalid args
        if arg1 == -1:
            embed = discord.Embed(
                title='No matching character found; try alternative spellings.\nRemember, the character\'s name must be one word.',
                color=0xEA7D07)
            await ctx.send(embed=embed)
        elif arg2 == -1:
            embed = discord.Embed(
                title='No matching stat found; try alternative spellings.\nRemember, the stat\'s name must be one word.',
                color=0xEA7D07)
            await ctx.send(embed=embed)

        # handle valid args
        else:
            stat_name = stats_lol[0][arg2]  # grab info from list of lists once valid name

            # handle highest, lowest, and average
            if arg1 < -1:
                result = CharacterStats.stat_logic(arg1, arg2, stat_name, stats_lol)
                embed = discord.Embed(title=result, color=0x1AA3E9)
                await ctx.send(embed=embed)

            # handle normal stat grabbing
            else:
                character_name = stats_lol[arg1][0]
                stat_val = stats_lol[arg1][arg2]
                embed = discord.Embed(title=f"{character_name}\'s {stat_name} is {stat_val}", color=0x1AA3E9)
                await ctx.send(embed=embed)

    # chemistry link chart
    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def chemistry(self, ctx):
        embed = discord.Embed()
        embed.add_field(name='CHARACTER CHEMISTRY CHART',
                        value='The following image displays the chemistry links between all characters with a value of 0 being the worst and 100 being the best:\n')
        embed.set_image(
            url="https://media.discordapp.net/attachments/628354009865912350/815693119348932628/image0.png?width=678&height=676")
        await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(GameStatLookup(client))
