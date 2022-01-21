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
    character = character.lower() # ignore case-sensitivity stuff
    stat = stat.lower() # ignore case-sensitivity stuff
    arg1 = CharacterStats.findCharacter(character) # returns row index of character
    arg2 = CharacterStats.findStat(stat) # returns column index of character

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



# message for helping new people figure out Rio
@bot.command()
async def rioGuide(ctx):
    await ctx.send('For a tutorial on setting up Project Rio, check out <#823805174811197470> or head to our website <https://www.projectrio.online/tutorial>\nIf you need further help, please use <#823805409143685130> to get assistance.')


# ball flickering
@bot.command()
async def flicker(ctx):
    await ctx.send('If you notice the ball flickering, you can solve the issue by changing your graphics backend.\n\n'
    'Open Rio, click graphics, then change the backend. The default is OpenGL. Vulkan or Direct3D11/12 should work, but which one specifically is different for each computer, so you will need to test that on your own')


# optimization guide
@bot.command()
async def optimize(ctx):
    await ctx.send('Many settings on Project Rio are already optimized ahead of time; however, there is no one-size-fits-all option for different computers. Here is a guide on optimization to help help you started\n> <https://www.projectrio.online/optimize>')


# tell what Rio is
@bot.command()
async def rio(ctx):
    await ctx.send('Project Rio is a custom build of Dolphin Emulator which is built specifically for Mario Superstar Baseball. It contains optimized online play, automatic stat tracking, built-in gecko codes, and soon will alos host a database and webapp on the website.\n\nYou can download it here: <:ProjectRio:866436395349180416>\n> <https://www.projectrio.online/>')


# gecko code info
@bot.command()
async def gecko(ctx):
    await ctx.send('Gecko Codes allow modders to inject their own assembly code into the game in order to create all of the mods we use.\n\n'
    'You can change which gecko codes are active by opening Project Rio and clicking the "Gecko Code" tab on the top of the window. Simply checko off which mods you want to use. You can obtain all of out gecko codes by clicking "Download Codes" at the bottom right corner of the Gecko Codes window.\n\n'
    '**NOTES**:\n-Do **NOT** disable any code which is labeled as "Required" otherwise many Project Rio functionalites will not work\n-If you run into bugs when using gecko codes, you may have too many turned on. Try turning off the Netplay Event Code\n-The Netplay Event Code is used for making online competitive games easy to set up. It is only required for ranked online games')


# guy.jpg
@bot.command()
async def guy(ctx):
    await ctx.send('<:Guy:927712162829451274>')


# peacock
@bot.command()
async def peacock(ctx):
    await ctx.send(':peacock:')
    

#Key given to bot through .env file so bot can run in server
bot.run(os.getenv('TOKEN'))