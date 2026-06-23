# file: RioBot.py
# authors: Kevin Malone / Cactus, Nick Taber / Pokebunny

import datetime
import logging
import os

import aiohttp
import discord
import pytz
from discord.ext import commands, tasks
from dotenv import load_dotenv
from helpers import offensive_stat_calcs, pitching_stat_calcs
from resources import ladders

logger = logging.getLogger(__name__)

_EST = pytz.timezone("America/New_York")
_CACHE_REFRESH_TIME = datetime.time(hour=6, minute=0, tzinfo=_EST)

# load .env file which has discord token

load_dotenv()
token = os.getenv("BOT_TOKEN")
intents = discord.Intents.all()

cog_files = [
    "web_stat_lookup",
    "game_stat_lookup",
    "misc",
    "memes",
    "randomize_commands",
    "ladder",
    "recent_games",
    "classic_teams",
    "submit_results",
    "registration",
    "matchmaking",
]


class RioBot(commands.Bot):
    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        ladders.set_session(self.session)
        for cog in cog_files:
            await self.load_extension("cogs." + cog)
            logger.info("%s cog loaded", cog)


# initialize the bot commands with the associated prefix
bot = RioBot(command_prefix="!", intents=intents, case_insensitive=True)


@bot.event
async def on_ready():
    logger.info("%s has connected to Discord!", bot.user)

    # Matchmaking (buttons + refresh loop) is owned by the matchmaking cog.

    # Start timed tasks — guarded so reconnects don't raise RuntimeError
    if not ladders.refresh_ladders.is_running():
        ladders.refresh_ladders.start()
    if not refresh_stat_caches.is_running():
        refresh_stat_caches.start()


@tasks.loop(time=_CACHE_REFRESH_TIME)
async def refresh_stat_caches():
    for mode in ladders.GAME_MODES:
        try:
            await offensive_stat_calcs.refresh_baselines(mode, bot.session)
            await pitching_stat_calcs.refresh_baselines(mode, bot.session)
        except Exception:
            logger.exception("Failed to refresh stat cache for %s", mode)


# Exception handler on user commands to bot
@bot.event
async def on_command_error(ctx, error):
    logger.warning("Command error in %s: %s", ctx.command, error)

    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(title=error, color=0xEA7D07)
        await ctx.send(embed=embed)

    elif isinstance(error, commands.UserInputError):
        if str(error) == "stat is a required argument that is missing.":
            embed = discord.Embed(title="You need to specify the stat you are looking up!", color=0xEA7D07)
            embed.add_field(name="Example:", value="!stat bowser power", inline=False)
            embed.add_field(name="Error:", value=str(error), inline=False)
            await ctx.send(embed=embed)
        elif str(error) == "character is a required argument that is missing.":
            embed = discord.Embed(title="You need to specify the character you are looking up!", color=0xEA7D07)
            embed.add_field(name="Example:", value="!stat bowser power", inline=False)
            embed.add_field(name="Error:", value=str(error), inline=False)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Something went wrong!", color=0xEA7D07)
            embed.add_field(name="Error:", value=str(error), inline=True)
            await ctx.send(embed=embed)

    elif isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title="The specified command does not exist!", color=0xEA7D07)
        embed.add_field(name="Error:", value=str(error), inline=True)
        await ctx.send(embed=embed)

    elif isinstance(error, commands.MissingRole):
        embed = discord.Embed(title=error, color=0xEA7D07)
        await ctx.send(embed=embed)

    else:
        embed = discord.Embed(title="Something went wrong!", color=0xEA7D07)
        embed.add_field(name="Error:", value=str(error), inline=True)
        await ctx.send(embed=embed)


# root_logger=True lets discord.py configure the root logger (timestamped
# StreamHandler at INFO) so our own module loggers are actually emitted, not
# just discord's. Without this our logger.info calls go nowhere.
bot.run(token, root_logger=True)
