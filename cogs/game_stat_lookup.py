import discord
from discord.ext import commands
from resources import EnvironmentVariables as ev

from resources import CharacterStats
from resources.characters import BAT_URLS

BOT_SPAM_CHANNEL_ID = int(ev.get_var("bot_spam_channel_id"))

stats_lol = []
CharacterStats.build_stats_lol(stats_lol)
CharacterStats.build_stat_objs()

NL = "\n"
stat_help_string = "This command lists out stat commands you can use and their functions." + NL \
                     + "Note that `<character>` can also be replaced by the following in some cases: `<best>` `<worst>` `<avg>`" + NL + NL \
                     + "**BATTING STATS**:" + NL \
                     + "`!stat <character> charge` ------- Returns the numeric charge hit power for that character" + NL \
                     + "`!stat <character> contact` ------ Returns the numeric slap hit power for that character" + NL \
                     + "`!stat <character> nice` --------- Returns the numeric nice contact zone for that character" + NL \
                     + "`!stat <character> perfect` ------ Returns the numeric perfect contact zone for that character" + NL \
                     + "`!stat <character> bunt` --------- Returns the numeric bunt stat for that character" + NL \
                     + "`!stat <character> traj` --------- Returns the type of trajectory for that character" + NL \
                     + "`!stat <character> starswing` ---- Returns the type of star swing that character has" + NL \
                     + "`!stat <character> cssbat` ------- Returns the numeric batting stat for that character as shown in game (1 to 10)" + NL + NL\
                     + "**PITCHING STATS**:" + NL \
                     + "`!stat <character> curvespeed` --- Returns the numeric curve pitch speed for that character" + NL \
                     + "`!stat <character> fastball` ----- Returns the numeric fastball pitch speed for that character" + NL \
                     + "`!stat <character> curve` -------- Returns the numeric curveball curve distance for that character" + NL \
                     + "`!stat <character> 0x2` ---------- Returns the numeric 'cursed ball' stat for that character" + NL \
                     + "`!stat <character> 0x4` ---------- Returns the numeric 0x4 stat for that character" + NL \
                     + "`!stat <character> starpitch` ---- Returns the type of star pitch that character has" + NL \
                     + "`!stat <character> csspitch` ----- Returns the numeric pitching stat for that character as shown in game (1 to 10)" + NL + NL\
                     + "**FIELDING STATS**:" + NL \
                     + "`!stat <character> arm` ---------- Returns the numeric arm strength for that character" + NL \
                     + "`!stat <character> dive` --------- Returns the numeric dive range for that character" + NL \
                     + "`!stat <character> radiusair` ---- Returns the numeric hitbox radius that character has when catching a fly ball" + NL \
                     + "`!stat <character> radiusground` - Returns the numeric hitbox radius that character has when catching a ground ball" + NL \
                     + "`!stat <character> height` ------- Returns the numeric height of that character" + NL \
                     + "`!stat <character> cssfield` ----- Returns the numeric fielding stat for that character as shown in game (1 to 10)" + NL + NL\
                     + "**BASERUNNING STATS**:" + NL \
                     + "`!stat <character> speed` -------- Returns the numeric running speed for that character" + NL \
                     + "`!stat <character> weight` ------- Returns the numeric weight of that character (0 to 4)" + NL \
                     + "`!stat <character> cssrun` ------- Returns the numeric fielding stat for that character as shown in game (1 to 10)" + NL + NL\
                     + "**OTHER STATS**:" + NL \
                     + "`!stat <character> class` -------- Returns the characters class as shown in game" + NL \

class GameStatLookup(commands.Cog):
    def __init__(self, client):
        self.client = client

    # stat help command
    @commands.command(help = "returns a display of all possible stat commands")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def stathelp(self, ctx):
        if ctx.channel.id == BOT_SPAM_CHANNEL_ID:
            embed = discord.Embed(title='How to use stat commands:', description=stat_help_string)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title='This command cannot be used in this channel:',
                description=f'Please use this command in the following channel: <#{BOT_SPAM_CHANNEL_ID}>',
                color=0xFF5733)
            await ctx.send(embed=embed)


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
    @commands.command(help = "returns chart for chemistry between characters")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def chemistry(self, ctx):
        embed = discord.Embed()
        embed.add_field(name='CHARACTER CHEMISTRY CHART',
                        value='The following image displays the chemistry links between all characters with a value of 0 being the worst and 100 being the best:\n')
        embed.set_image(
            url="https://media.discordapp.net/attachments/628354009865912350/815693119348932628/image0.png?width=678&height=676")
        await ctx.send(embed=embed)

    @commands.command(help = "type !bat <character name> for image of character's bat")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def bat(self, ctx, character: str):
        character = character.lower()  # ignore case-sensitivity stuff
        arg1 = CharacterStats.find_character(character)  # returns row index of character

        # check for invalid args
        if arg1 <= -1:
            embed = discord.Embed(
                title='No matching character found; try alternative spellings.\nRemember, the character\'s name must be one word.',
                color=0xEA7D07)
            await ctx.send(embed=embed)

        # handle valid args
        else:
            characterName = stats_lol[arg1][0]
            embed = discord.Embed(title=f"{characterName}\'s Bat", color=0x1AA3E9)
            embed.set_image(url=BAT_URLS[arg1 - 1])
            await ctx.send(embed=embed)

async def setup(client):
    await client.add_cog(GameStatLookup(client))
