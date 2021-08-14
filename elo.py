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
    botReaction = await ctx.send(embed=embed)
    checkEmoji = "\U00002705"
    exEmoji = "\U0000274C"
    await botReaction.add_reaction(checkEmoji)
    await botReaction.add_reaction(exEmoji)

    def check(reaction, user):
        return user == loserUser and str(reaction.emoji) in [checkEmoji]

    confirmation = await bot.wait_for("reaction_add",check=check)

    if confirmation:
        embed=discord.Embed(title= 'Confirmed match between ' + f'{winnerUser.name}' + ' and ' + f'{loserUser.name}' + '!' , color=0x138F13)
        await ctx.send(embed=embed)

bot.run(os.getenv('TOKEN'))