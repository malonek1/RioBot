import os
import discord
from discord.ext import commands
import random

intents = discord.Intents.all()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', description='simple command bot', intents=intents)

quoteMap = {}

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

@bot.command()
async def add(ctx, *, quote: str):
    sender = ctx.author.name
    quoteMap[quote] = sender
    embed=discord.Embed(title= sender +' has added the following quote: ', description= '"' + quote + '"', color=0x00C940)
    await ctx.send(embed=embed)

@bot.command()
async def quote(ctx):
    quoteDescription, quoteAuthor = random.choice(list(quoteMap.items()))
    embed=discord.Embed(description='by ' + quoteAuthor ,title='"' + quoteDescription + '"', color=0xFF5733)
    await ctx.send(embed=embed)

@bot.command()
async def guide(ctx):
    embed=discord.Embed(title= 'Try the following commands: ', color=0xDAC600)
    embed.add_field(name="!add", value="Adds a quote", inline=False)
    embed.add_field(name="!guide", value="Brings up list of commands", inline=False)
    embed.add_field(name="!quote", value="Displays a random quote", inline=False)
    await ctx.send(embed=embed)

#@bot.command()
#async def quote(ctx, member : discord.Member):
#    if(member.display_name == "Admit"):
#        await ctx.send("Nice try Benny")
#    else:
#        await ctx.send('"' + random.choice(quotes) + '"')

bot.run(os.getenv('TOKEN'))