# file: RioBot.py
# author: Nick Taber / Pokebunny
# version: 11/26/22

import os

from discord.ext import commands
from dotenv import load_dotenv
import discord

from resources import gspread_client
import matchmaking as mm

# load .env file which has discord token

load_dotenv()
token = os.getenv("BOT_TOKEN")
intents = discord.Intents.all()

# initialize the bot commands with the associated prefix
bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")

    # Initialize matchmaking buttons
    await mm.init_buttons(bot)

    # Start timed tasks
    mm.refresh_queue.start(bot)
    gspread_client.refresh_api_data.start()

    cog_files = ["web_stat_lookup", "game_stat_lookup", "misc", "submit_results", "memes"]

    for cog in cog_files:
        await bot.load_extension("cogs." + cog)
        print("%s has loaded." % cog)


# Exception handler on user commands to bot
@bot.event
async def on_command_error(ctx, error):
    print(error)

    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(title=error, color=0xEA7D07)
        await ctx.send(embed=embed)

    elif isinstance(error, commands.UserInputError):
        if str(error) == "stat is a required argument that is missing.":
            embed = discord.Embed(title='You need to specify the stat you are looking up!', color=0xEA7D07)
            embed.add_field(name='Example:', value='!stat bowser power', inline=False)
            embed.add_field(name='Error:', value=str(error), inline=False)
            await ctx.send(embed=embed)
        elif str(error) == "character is a required argument that is missing.":
            embed = discord.Embed(title='You need to specify the character you are looking up!', color=0xEA7D07)
            embed.add_field(name='Example:', value='!stat bowser power', inline=False)
            embed.add_field(name='Error:', value=str(error), inline=False)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title='Please specify your score, your opponents score, and tag your opponent',
                                  color=0xEA7D07)
            embed.add_field(name='Example:', value='!submit 12 5 @user', inline=True)
            embed.add_field(name='Error:', value=str(error), inline=True)
            await ctx.send(embed=embed)

    elif isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title='The specified command does not exist!', color=0xEA7D07)
        embed.add_field(name='Error:', value=str(error), inline=True)
        await ctx.send(embed=embed)

    elif isinstance(error, commands.MissingRole):
        embed = discord.Embed(title=error, color=0xEA7D07)
        await ctx.send(embed=embed)

    else:
        embed = discord.Embed(title='Something went wrong!', color=0xEA7D07)
        embed.add_field(name='Error:', value=str(error), inline=True)
        await ctx.send(embed=embed)


bot.run(token)
