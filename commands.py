import os
import discord
from discord.ext import commands
import random

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', description='simple command bot', intents=intents)

quotes = []

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

@bot.command()
async def add(ctx, quote : str):
    quotes.append(quote)
    await ctx.send('Added quote: ' + '"' + quote + '"')

@bot.command()
async def quote(ctx):
     await ctx.send('"' + random.choice(quotes) + '"')

#@bot.command()
#async def quote(ctx, member : discord.Member):
#    if(member.display_name == "Admit"):
#        await ctx.send("Nice try Benny")
#    else:
#        await ctx.send('"' + random.choice(quotes) + '"')


bot.run(os.getenv('TOKEN'))