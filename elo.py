import os
import asyncio
from SheetsParser import EloSheetsParser
import CharacterStats
#Creation of sheets Object:
#sheetParser = EloSheetsParser('MSSB')

#discord.py imports:
import discord
from discord.ext import commands
#Creation of discord bot
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', description='simple command bot', intents=intents)

statsLoL = []

#Logging message to indicate bot is up and running
# build stat objects from csv's
@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    CharacterStats.buildStatsLoL(statsLoL)
    CharacterStats.buildStatObjs()

#Exception handler on user commands to bot
@bot.event
async def on_command_error(ctx, error):
    print(error)
    embed=discord.Embed(title= 'Please specify your score, your opponents score, and tag your opponent', color=0xEA7D07)
    embed.add_field(name= 'Example:', value= '!submit 12 5 @user' , inline=True)
    await ctx.send(embed=embed)

#Submit user command that allows a player to submit a game with another player
@bot.command()
async def submit(ctx, submiterScore: int, oppScore: int, oppUser: discord.Member):
    #Check to make sure that runs values input by user are between 0 and 99
    if (submiterScore < 0) or (oppScore < 0) or (submiterScore > 99) or (oppScore > 99):
        embed=discord.Embed(title= 'Scores must be between 0 and 100!', color=0xEA7D07)
        await ctx.send(embed=embed)
    else:
        #Initial bot message displayed for game submitted by primary user
        submiterUser = ctx.author
        embed=discord.Embed(title= f'{oppUser.name} confirm these results by reacting with :white_check_mark: or reject the results with :x: ', color=0xC496EF)
        embed.add_field(name= f'{submiterUser.name}:', value= submiterScore, inline=False)
        embed.add_field(name= f'{oppUser.name}:', value= oppScore, inline=True)
        botReaction = await ctx.send(embed=embed)
        checkEmoji = "\U00002705"
        exEmoji = "\U0000274C"
        await botReaction.add_reaction(checkEmoji)
        await botReaction.add_reaction(exEmoji)

        #Check for bot to see if a user confirmed or denied the results submitted by another user
        def checkConfirm(reaction, user):
            return user == oppUser and (str(reaction.emoji) in [checkEmoji] or str(reaction.emoji) in [exEmoji])

        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=checkConfirm)
        except asyncio.TimeoutError:
            #If user doesn't react to message within 1 minute, initial message is deleted
            await botReaction.delete()
            embed=discord.Embed(title= 'Cancelled match between ' + f'{submiterUser.name}' + ' and ' + f'{oppUser.name}' + ' for not reacting in time!' , color=0xFF5733)
            await ctx.send(embed=embed)
        else:
            #Confirmation message displays if secondary user reacts with check mark
            if reaction.emoji == checkEmoji:
                embed=discord.Embed(title= 'Confirmed match between ' + f'{submiterUser.name}' + ' and ' + f'{oppUser.name}' + '!' , color=0x138F13)
                await ctx.send(embed=embed)

                #Update Spreadsheet
                if submiterScore > oppScore:
                    print('Submitter Wins!')
                    sheetParser.confirmMatch(f'{submiterUser}', f'{oppUser}', submiterScore, oppScore)
                elif submiterScore < oppScore:
                    print('Opponent Wins!')
                    sheetParser.confirmMatch(f'{oppUser}', f'{submiterUser}', oppScore, submiterScore)
            #Rejection message displays if secondary user reacts with an X mark
            elif reaction.emoji == exEmoji:
                embed=discord.Embed(title= 'Cancelled match between ' + f'{submiterUser.name}' + ' and ' + f'{oppUser.name}' + '!' , color=0xFF5733)
                await ctx.send(embed=embed)


# Stats command
# Character is either the character who's stat you want or "highest", "lowest", "average"
# Stat is the stat you want to grab
@bot.command()
async def stat(ctx, character: str, stat: str):
    arg1 = CharacterStats.findCharacter(character) # returns row index of character
    arg2 = CharacterStats.findStat(stat) # returns column index of character
    character = character.lower() # ignore case-sensitivity stuff
    stat = stat.lower() # ignore case-sensitivity stuff

    # check for invalid args
    if arg1 == -1:
        await ctx.send('No matching character found; try alternative spellings.\nRemember, the character\'s name must be one word.')
    elif arg2 == -1:
        await ctx.send('No matching stat found; try alternative spellings.\nRemember, the stat\'s name must be one word.')
    
    # handle valid args
    else:
        statName = statsLoL[0][arg2] # grab info from list of lists once valid name

        # handle highest, lowest, and average
        if arg1 < -1:
            result = CharacterStats.statLogic(arg1, arg2, statName, statsLoL)
            await ctx.send(result)

        # handle normal stat grabbing
        else:
            characterName = statsLoL[arg1][0]
            statVal = statsLoL[arg1][arg2]
            await ctx.send(characterName + '\'s ' + statName + ' is ' + str(statVal))
            

#Key given to bot through .env file so bot can run in server
bot.run(os.getenv('TOKEN'))