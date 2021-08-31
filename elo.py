import os
import asyncio
from SheetsParser import SheetsParser

#discord.py imports:
import discord
from discord.ext import commands
#Creation of discord bot
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', description='simple command bot', intents=intents)

#Google Sheets imports:
import gspread
#Creation of gspread object
client = gspread.service_account()
sheet = client.open('MSSB Elo').sheet1

sheetParser = SheetsParser('MSSB')

#Logging message to indicate bot is up and running
@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

#Exception handler on user commands to bot
@bot.event
async def on_command_error(ctx, error):
    embed=discord.Embed(title= 'Please specify your score, your opponents score, and tag your opponent', color=0xEA7D07)
    embed.add_field(name= 'Example:', value= '!submit 12 5 @user' , inline=True)
    await ctx.send(embed=embed)

#Submit user command that allows a player to submit a game with another player
@bot.command()
async def submit(ctx, winnerScore: int, loserScore: int, loserUser: discord.Member):
    #Check to make sure that runs values input by user are between 0 and 99
    if (winnerScore < 0) or (loserScore < 0) or (winnerScore > 99) or (loserScore > 99):
        embed=discord.Embed(title= 'Scores must be between 0 and 100!', color=0xEA7D07)
        await ctx.send(embed=embed)
    else:
        #Initial bot message displayed for game submitted by primary user
        winnerUser = ctx.author
        embed=discord.Embed(title= f'{loserUser.name} confirm these results by reacting with :white_check_mark: or reject the results with :x: ', color=0xC496EF)
        embed.add_field(name= f'{winnerUser.name}:', value= winnerScore, inline=False)
        embed.add_field(name= f'{loserUser.name}:', value= loserScore, inline=True)
        botReaction = await ctx.send(embed=embed)
        checkEmoji = "\U00002705"
        exEmoji = "\U0000274C"
        await botReaction.add_reaction(checkEmoji)
        await botReaction.add_reaction(exEmoji)

        #Check for bot to see if a user confirmed or denied the results submitted by another user
        def checkConfirm(reaction, user):
            return user == loserUser and (str(reaction.emoji) in [checkEmoji] or str(reaction.emoji) in [exEmoji])

        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=checkConfirm)
        except asyncio.TimeoutError:
            #If user doesn't react to message within 1 minute, initial message is deleted
            await botReaction.delete()
            embed=discord.Embed(title= 'Cancelled match between ' + f'{winnerUser.name}' + ' and ' + f'{loserUser.name}' + ' for not reacting in time!' , color=0xFF5733)
            await ctx.send(embed=embed)
        else:
            #Confirmation message displays if secondary user reacts with check mark
            if reaction.emoji == checkEmoji:
                embed=discord.Embed(title= 'Confirmed match between ' + f'{winnerUser.name}' + ' and ' + f'{loserUser.name}' + '!' , color=0x138F13)
                await ctx.send(embed=embed)

                #Update Spreadsheet
                sheetParser.confirmMatch(f'{winnerUser.name}', f'{loserUser.name}', winnerScore, loserScore)

            #Rejection message displays if secondary user reacts with an X mark
            elif reaction.emoji == exEmoji:
                embed=discord.Embed(title= 'Cancelled match between ' + f'{winnerUser.name}' + ' and ' + f'{loserUser.name}' + '!' , color=0xFF5733)
                await ctx.send(embed=embed)

#Key given to bot through .env file so bot can run in server
bot.run(os.getenv('TOKEN'))