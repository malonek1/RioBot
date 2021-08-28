import os
import discord
import asyncio
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', description='simple command bot', intents=intents)

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

@bot.event
async def on_command_error(ctx, error):
    embed=discord.Embed(title= 'Please specify your score, your opponents score, and tag your opponent', color=0xEA7D07)
    embed.add_field(name= 'Example:', value= '!submit 12 5 @user' , inline=True)
    await ctx.send(embed=embed)

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

    def checkConfirm(reaction, user):
        return user == loserUser and (str(reaction.emoji) in [checkEmoji] or str(reaction.emoji) in [exEmoji])

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=10.0, check=checkConfirm)
    except asyncio.TimeoutError:
        await botReaction.delete()
        embed=discord.Embed(title= 'Cancelled match between ' + f'{winnerUser.name}' + ' and ' + f'{loserUser.name}' + ' for not reacting in time!' , color=0xFF5733)
        await ctx.send(embed=embed)
    else:
        if reaction.emoji == checkEmoji:
            embed=discord.Embed(title= 'Confirmed match between ' + f'{winnerUser.name}' + ' and ' + f'{loserUser.name}' + '!' , color=0x138F13)
            await ctx.send(embed=embed)
        elif reaction.emoji == exEmoji:
            embed=discord.Embed(title= 'Cancelled match between ' + f'{winnerUser.name}' + ' and ' + f'{loserUser.name}' + '!' , color=0xFF5733)
            await ctx.send(embed=embed)

bot.run(os.getenv('TOKEN'))