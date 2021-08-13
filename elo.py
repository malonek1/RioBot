import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', description='simple command bot', intents=intents)

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

@bot.command()
async def submit(ctx, winnerScore: int, loserScore: int, loserUser: discord.Member):
    winnerUser = ctx.author
    embed=discord.Embed(title= f'{loserUser.name} confirm these results by reacting with :white_check_mark: or reject the results with :x: ', color=0xC496EF)
    embed.add_field(name= f'{winnerUser.name}:', value= winnerScore, inline=False)
    embed.add_field(name= f'{loserUser.name}:', value= loserScore, inline=True)
    await ctx.send(embed=embed)
    checkEmoji = "\U0001F642"
    await ctx.message.add_reaction(checkEmoji)


bot.run(os.getenv('TOKEN'))