import os
from dotenv import load_dotenv
import asyncio
from SheetsParser import EloSheetsParser
import CharacterStats
#Creation of sheets Object:
sheetParser = EloSheetsParser('MSSB')

#discord.py imports:
import discord
from discord.ext import commands
#Creation of discord bot
load_dotenv()
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', description='simple command bot', intents=intents)

#csv initialization
statsLoL = []

#Logging message to indicate bot is up and running
# build stat objects from csv's
@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    CharacterStats.buildStatsLoL(statsLoL)
    CharacterStats.buildStatObjs()

# Exception handler on user commands to bot
@bot.event
async def on_command_error(ctx, error):
    print(error)

    if isinstance(error, commands.CommandOnCooldown):
        embed=discord.Embed(title=error, color=0xEA7D07)
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
            embed=discord.Embed(title= 'Please specify your score, your opponents score, and tag your opponent', color=0xEA7D07)
            embed.add_field(name= 'Example:', value= '!submit 12 5 @user' , inline=True)
            embed.add_field(name='Error:', value=str(error), inline=True)
            await ctx.send(embed=embed)

    elif isinstance(error, commands.CommandNotFound):
        embed=discord.Embed(title= 'The specified command does not exist!', color=0xEA7D07)
        embed.add_field(name= 'Error:', value= str(error) , inline=True)
        await ctx.send(embed=embed)

    elif isinstance(error, commands.MissingRole):
        embed=discord.Embed(title=error, color=0xEA7D07)
        await ctx.send(embed=embed)

    else:
        embed=discord.Embed(title= 'Something went wrong!', color=0xEA7D07)
        embed.add_field(name='Error:', value=str(error), inline=True)
        await ctx.send(embed=embed)


# Submit user command that allows a player to submit a game with another player
@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def submit(ctx, submiterScore: int, oppScore: int, oppUser: discord.Member):
    if ctx.channel.id == 947699610921599006:
        # Check to make sure that runs values input by user are between 0 and 99
        if (submiterScore < 0) or (oppScore < 0) or (submiterScore > 99) or (oppScore > 99):
            embed=discord.Embed(title= 'Scores must be between 0 and 100!', color=0xEA7D07)
            await ctx.send(embed=embed)
        else:
            #Initial bot message displayed for game submitted by primary user
            submiterUser = ctx.author
            if submiterUser == oppUser:
                embed=discord.Embed(title= 'You cannot submit a game against yourself!', color=0xEA7D07)
                await ctx.send(embed=embed)
            else:
                embed=discord.Embed(title= 'Are you submitting to the Stars-On leaderboards or the Stars-Off leaderboards?', color=0xC496EF)
                embed.add_field(name='STARS-OFF', value=':goat:', inline=True)
                embed.add_field(name='STARS-ON', value=':star:', inline=True)
                botStarReaction = await ctx.send(embed=embed)
                starEmoji = "\U00002B50"
                goatEmoji = "\U0001F410"
                await botStarReaction.add_reaction(goatEmoji)
                await botStarReaction.add_reaction(starEmoji)

                def checkStar(reaction, user):
                    return user == submiterUser and (str(reaction.emoji) in [starEmoji] or str(reaction.emoji) in [goatEmoji])

                try:
                    reaction, user = await bot.wait_for('reaction_add', timeout=300.0, check=checkStar)
                except asyncio.TimeoutError:
                    #If user doesn't react to message within 1 minute, initial message is deleted
                    await botStarReaction.delete()
                    embed=discord.Embed(title= 'Cancelled Stars-ON match between ' + f'{submiterUser.name}' + ' and ' + f'{oppUser.name}' + ' for not reacting in time!' , color=0xFF5733)
                    await ctx.send(embed=embed)
                else:
                    if reaction.emoji == starEmoji:
                        embed=discord.Embed(title= f'{oppUser.name}, confirm the results of your Stars-On :star: game by reacting with :white_check_mark: or reject the results with :x: ', color=0xC496EF)
                        embed.add_field(name= f'{submiterUser.name} score:', value= submiterScore, inline=True)
                        embed.add_field(name= f'{oppUser.name} score:', value= oppScore, inline=True)
                        botReaction = await ctx.send(embed=embed)
                        checkEmoji = "\U00002705"
                        exEmoji = "\U0000274C"
                        await botReaction.add_reaction(checkEmoji)
                        await botReaction.add_reaction(exEmoji)

                        #Check for bot to see if a user confirmed or denied the results submitted by another user
                        def checkConfirm(reaction, user):
                            if user == oppUser and (str(reaction.emoji) in [checkEmoji] or str(reaction.emoji) in [exEmoji]):
                                return user == oppUser and (str(reaction.emoji) in [checkEmoji] or str(reaction.emoji) in [exEmoji])
                            elif user == submiterUser and (str(reaction.emoji) in [exEmoji]):
                                return user == submiterUser and (str(reaction.emoji) in [exEmoji])
                        try:
                            reaction, user = await bot.wait_for('reaction_add', timeout=300.0, check=checkConfirm)
                        except asyncio.TimeoutError:
                            #If user doesn't react to message within 1 minute, initial message is deleted
                            await botStarReaction.delete()
                            await botReaction.delete()
                            embed=discord.Embed(title= 'Cancelled Stars-ON match between ' + f'{submiterUser.name}' + ' and ' + f'{oppUser.name}' + ' for not reacting in time!' , color=0xFF5733)
                            await ctx.send(embed=embed)
                        else:
                            #Confirmation message displays if secondary user reacts with check mark
                            if reaction.emoji == checkEmoji:
                                await botStarReaction.delete()
                                await botReaction.delete()
                                embed=discord.Embed(title= 'Confirmed Stars-ON match between ' + f'{submiterUser.name}' + ' and ' + f'{oppUser.name}' + '!' , color=0x138F13)
                                await ctx.send(embed=embed)

                                #Update Spreadsheet
                                if submiterScore > oppScore:
                                    print('Submitter Wins!')
                                    sheetParser.confirmMatch(f'{submiterUser.name}', f'{oppUser.name}', f'{submiterUser.id}', f'{oppUser.id}', submiterScore, oppScore, 'ON')
                                elif submiterScore < oppScore:
                                    print('Opponent Wins!')
                                    sheetParser.confirmMatch(f'{oppUser.name}', f'{submiterUser.name}', f'{oppUser.id}', f'{submiterUser.id}', oppScore, submiterScore, 'ON')
                            #Rejection message displays if secondary user reacts with an X mark
                            elif reaction.emoji == exEmoji:
                                await botStarReaction.delete()
                                await botReaction.delete()
                                embed=discord.Embed(title= 'Cancelled Stars-ON match between ' + f'{submiterUser.name}' + ' and ' + f'{oppUser.name}' + '!' , color=0xFF5733)
                                await ctx.send(embed=embed)

                    elif reaction.emoji == goatEmoji:
                        embed=discord.Embed(title= f'{oppUser.name}, confirm the results of your Stars-Off :goat: game by reacting with :white_check_mark: or reject the results with :x: ', color=0xC496EF)
                        embed.add_field(name= f'{submiterUser.name} score:', value= submiterScore, inline=False)
                        embed.add_field(name= f'{oppUser.name} score:', value= oppScore, inline=True)
                        botReaction = await ctx.send(embed=embed)
                        checkEmoji = "\U00002705"
                        exEmoji = "\U0000274C"
                        await botReaction.add_reaction(checkEmoji)
                        await botReaction.add_reaction(exEmoji)

                        #Check for bot to see if a user confirmed or denied the results submitted by another user
                        def checkConfirm(reaction, user):
                            if user == oppUser and (str(reaction.emoji) in [checkEmoji] or str(reaction.emoji) in [exEmoji]):
                                return user == oppUser and (str(reaction.emoji) in [checkEmoji] or str(reaction.emoji) in [exEmoji])
                            elif user == submiterUser and (str(reaction.emoji) in [exEmoji]):
                                return user == submiterUser and (str(reaction.emoji) in [exEmoji])
                        try:
                            reaction, user = await bot.wait_for('reaction_add', timeout=300.0, check=checkConfirm)
                        except asyncio.TimeoutError:
                            #If user doesn't react to message within 1 minute, initial message is deleted
                            await botStarReaction.delete()
                            await botReaction.delete()
                            embed=discord.Embed(title= 'Cancelled Stars-OFF match between ' + f'{submiterUser.name}' + ' and ' + f'{oppUser.name}' + ' for not reacting in time!' , color=0xFF5733)
                            await ctx.send(embed=embed)
                        else:
                            #Confirmation message displays if secondary user reacts with check mark
                            if reaction.emoji == checkEmoji:
                                await botStarReaction.delete()
                                await botReaction.delete()
                                embed=discord.Embed(title= 'Confirmed Stars-OFF match between ' + f'{submiterUser.name}' + ' and ' + f'{oppUser.name}' + '!' , color=0x138F13)
                                await ctx.send(embed=embed)

                                #Update Spreadsheet
                                if submiterScore > oppScore:
                                    print('Submitter Wins!')
                                    sheetParser.confirmMatch(f'{submiterUser.name}', f'{oppUser.name}', f'{submiterUser.id}', f'{oppUser.id}', submiterScore, oppScore, 'OFF')
                                elif submiterScore < oppScore:
                                    print('Opponent Wins!')
                                    sheetParser.confirmMatch(f'{oppUser.name}', f'{submiterUser.name}', f'{oppUser.id}', f'{submiterUser.id}', oppScore, submiterScore, 'OFF')
                            #Rejection message displays if secondary user reacts with an X mark
                            elif reaction.emoji == exEmoji:
                                await botStarReaction.delete()
                                await botReaction.delete()
                                embed=discord.Embed(title= 'Cancelled Stars-OFF match between ' + f'{submiterUser.name}' + ' and ' + f'{oppUser.name}' + '!' , color=0xFF5733)
                                await ctx.send(embed=embed)
    else:
        embed = discord.Embed(color=0xEA7D07)
        embed.add_field(name='The !submit command must be used here:', value='<#947699610921599006>')
        await ctx.send(embed=embed)


@bot.command()
@commands.has_any_role("Admins", "Moderator", "Bot Developer")
async def forceSubmit(ctx, firstScore: int, secondScore: int, firstUser: discord.Member, secondUser: discord.Member):
    if ctx.channel.id == 947699610921599006:
        # Check to make sure that runs values input by user are between 0 and 99
        if (firstScore < 0) or (secondScore < 0) or (firstScore > 99) or (secondScore > 99):
            embed=discord.Embed(title= 'Scores must be between 0 and 100!', color=0xEA7D07)
            await ctx.send(embed=embed)
        else:
            embed=discord.Embed(title= 'Are you submitting to the Stars-On leaderboards or the Stars-Off leaderboards?', color=0xC496EF)
            embed.add_field(name='STARS-OFF', value=':goat:', inline=True)
            embed.add_field(name='STARS-ON', value=':star:', inline=True)
            botStarReaction = await ctx.send(embed=embed)
            starEmoji = "\U00002B50"
            goatEmoji = "\U0001F410"
            await botStarReaction.add_reaction(goatEmoji)
            await botStarReaction.add_reaction(starEmoji)

            def checkStar(reaction, user):
                return user == ctx.author and (str(reaction.emoji) in [starEmoji] or str(reaction.emoji) in [goatEmoji])

            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=300.0, check=checkStar)
            except asyncio.TimeoutError:
                # If user doesn't react to message within 1 minute, initial message is deleted
                await botStarReaction.delete()
                embed = discord.Embed(
                    title='Cancelled match between ' + f'{submiterUser.name}' + ' and ' + f'{oppUser.name}' + ' for not reacting in time!',
                    color=0xFF5733)
                await ctx.send(embed=embed)

            if reaction.emoji == starEmoji:
                await botStarReaction.delete()
                embed = discord.Embed(title='Confirmed Stars-ON match between ' + f'{secondUser.name}' + ' and ' + f'{firstUser.name}' + '!', color=0x138F13)
                await ctx.send(embed=embed)
                if firstScore > secondScore:
                    print('Submitter Wins!')
                    sheetParser.confirmMatch(f'{firstUser.name}', f'{secondUser.name}', f'{firstUser.id}',
                                             f'{secondUser.id}', firstScore, secondScore, 'ON')
                elif firstScore < secondScore:
                    print('Opponent Wins!')
                    sheetParser.confirmMatch(f'{secondUser.name}', f'{firstUser.name}', f'{secondUser.id}',
                                             f'{firstUser.id}', secondScore, firstScore, 'ON')

            elif reaction.emoji == goatEmoji:
                await botStarReaction.delete()
                embed = discord.Embed(title='Confirmed Stars-OFF match between ' + f'{secondUser.name}' + ' and ' + f'{firstUser.name}' + '!', color=0x138F13)
                await ctx.send(embed=embed)
                if firstScore > secondScore:
                    print('Submitter Wins!')
                    sheetParser.confirmMatch(f'{firstUser.name}', f'{secondUser.name}', f'{firstUser.id}',
                                             f'{secondUser.id}', firstScore, secondScore, 'OFF')
                elif firstScore < secondScore:
                    print('Opponent Wins!')
                    sheetParser.confirmMatch(f'{secondUser.name}', f'{firstUser.name}', f'{secondUser.id}',
                                             f'{firstUser.id}', secondScore, firstScore, 'OFF')
    else:
        embed = discord.Embed(color=0xEA7D07)
        embed.add_field(name='The !submit command must be used here:', value='<#947699610921599006>')
        await ctx.send(embed=embed)

# Stats command
# Character is either the character who's stat you want or "highest", "lowest", "average"
# Stat is the stat you want to grab
@bot.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def stat(ctx, character: str, stat: str):
    character = character.lower() # ignore case-sensitivity stuff
    stat = stat.lower() # ignore case-sensitivity stuff
    arg1 = CharacterStats.findCharacter(character) # returns row index of character
    arg2 = CharacterStats.findStat(stat) # returns column index of character

    # check for invalid args
    if arg1 == -1:
        embed=discord.Embed(title = 'No matching character found; try alternative spellings.\nRemember, the character\'s name must be one word.', color=0xEA7D07)
        await ctx.send(embed=embed)
    elif arg2 == -1:
        embed=discord.Embed(title = 'No matching stat found; try alternative spellings.\nRemember, the stat\'s name must be one word.', color=0xEA7D07)
        await ctx.send(embed=embed)
    
    # handle valid args
    else:
        statName = statsLoL[0][arg2] # grab info from list of lists once valid name

        # handle highest, lowest, and average
        if arg1 < -1:
            result = CharacterStats.statLogic(arg1, arg2, statName, statsLoL)
            embed=discord.Embed(title = result, color=0x1AA3E9)
            await ctx.send(embed=embed)

        # handle normal stat grabbing
        else:
            characterName = statsLoL[arg1][0]
            statVal = statsLoL[arg1][arg2]
            embed=discord.Embed(title = f"{characterName}\'s {statName} is {statVal}", color=0x1AA3E9)
            await ctx.send(embed=embed)



# message for helping new people figure out Rio
@bot.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def rioGuide(ctx):
    embed=discord.Embed()
    embed.add_field(name = 'RIO GUIDE:', value = 'For a tutorial on setting up Project Rio, check out <#823805174811197470> or head to our website <https://www.projectrio.online/tutorial>\nIf you need further help, please use <#823805409143685130> to get assistance.')
    await ctx.send(embed=embed)

@bot.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def rayveean(ctx):
    embed=discord.Embed()
    embed.add_field(name = 'RAYVEEAN HURT MY FEELINGS:', value = "Rayveean changed my name to dignus and it really hurts my feelings inside. But I won't admit that to him because that would be embarassing")
    await ctx.send(embed=embed)


# ball flickering
@bot.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def flicker(ctx):
    embed=discord.Embed()
    embed.add_field(name = 'HOW TO FIX FLICKER ISSUE:', value= 'If you notice the ball flickering, you can solve the issue by changing your graphics backend.\n\n'
    'Open Rio, click graphics, then change the backend. The default is OpenGL. Vulkan or Direct3D11/12 should work, but which one specifically is different for each computer, so you will need to test that on your own')
    await ctx.send(embed=embed)


# optimization guide
@bot.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def optimize(ctx):
    embed=discord.Embed()
    embed.add_field(name = 'OPTIMIZING PROJECT RIO:', value = 'Many settings on Project Rio are already optimized ahead of time; however, there is no one-size-fits-all option for different computers. Here is a guide on optimization to help help you started\n> <https://www.projectrio.online/optimize>')
    await ctx.send(embed=embed)


# tell what Rio is
@bot.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def rio(ctx):
    embed=discord.Embed()
    embed.add_field(name = 'PROJECT RIO:', value = 'Project Rio is a custom build of Dolphin Emulator which is built specifically for Mario Superstar Baseball. It contains optimized online play, automatic stat tracking, built-in gecko codes, and soon will alos host a database and webapp on the website.\n\nYou can download it here: <:ProjectRio:866436395349180416>\n> <https://www.projectrio.online/>')
    await ctx.send(embed=embed)


# gecko code info
@bot.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def gecko(ctx):
    embed=discord.Embed()
    embed.add_field(name = 'GECKO CODES:', value = 'Gecko Codes allow modders to inject their own assembly code into the game in order to create all of the mods we use.\n\n'
    'You can change which gecko codes are active by opening Project Rio and clicking the "Gecko Code" tab on the top of the window. Simply checko off which mods you want to use. You can obtain all of out gecko codes by clicking "Download Codes" at the bottom right corner of the Gecko Codes window.\n\n'
    '**NOTES**:\n-Do **NOT** disable any code which is labeled as "Required" otherwise many Project Rio functionalites will not work\n-If you run into bugs when using gecko codes, you may have too many turned on. Try turning off the Netplay Event Code\n-The Netplay Event Code is used for making online competitive games easy to set up. It is only required for ranked online games')
    await ctx.send(embed=embed)


# guy.jpg
@bot.command()
async def guy(ctx):
    await ctx.send('<:Guy:927712162829451274>')


# peacock
@bot.command()
async def peacock(ctx):
    await ctx.send(':peacock:')

# goombo
@bot.command()
async def dingus(ctx):
    await ctx.send('<:goombo:987231921916510228>')


# inform users about roles
@bot.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def roles(ctx):
    embed=discord.Embed()
    embed.add_field(name = 'ROLES:', value = 'Set roles for yourself in <#945478927214866522>!')
    await ctx.send(embed=embed)


# explain auto golf mode
@bot.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def golf(ctx):
    embed=discord.Embed()
    embed.add_field(name = 'AUTO GOLF MODE:', value = 'Auto Golf Mode is the specific type of netcode that Project Rio uses for playing games online. It works giving one player 0 latency (the golfer) while the other player '
    '(the non-golfer) has an extra latency penalty.\n\nAuto Golf Mode automatically sets the batter to the golfer while in the pitching/batting state of the game, and then swaps the fielder to the golfer while in the fielding/baserunning state.')
    await ctx.send(embed=embed)


# ranked mode
@bot.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def ranked(ctx):
    embed=discord.Embed()
    embed.add_field(name = 'RANKED:', value = 'We run a ranked online ladder through this server. You can find the ranked leaderboards here: https://docs.google.com/spreadsheets/d/1B03IEnfOo3pAG7wBIjDW6jIHP0CTzn7jQJuxlNJebgc/edit?usp=sharing\n\n'
    'Our full ruleset can be seen in <#841761307245281320>. To play a ranked game, head to the <#948321928760918087> channel and look for games. Make sure ranked mode is enabled in the netplay lobby by checking the Ranked Box.\n'
    'After the game completes, use <#947699610921599006> to submit the game result to our leaderboard. Use the following command format:\n!submit <your score> <opponent\'s score> <@opponent\'s discord>')
    await ctx.send(embed=embed)


# nolan draft
@bot.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def nolan(ctx):
    embed=discord.Embed()
    embed.add_field(name = 'NOLAN DRAFT:', value = 'Nolan Draft is the competitive drafting format.\nStart with a coin flip. Winner gets choice of either choosing between being the home/away team or having the first/second pick.\n\n'
    'After deciding on this, the player with first pick gets one character pick, then playes alternate with picks of 2 until both teams are filled out. Under Nolan Draft, you do not have to pick a captain first. Players also choose'
    'a captain after drafting their full team. If playing with superstar characters off, bowser must be captain if chosen.\n\nAn infographic can be seen here:')
    embed.set_image(url="https://cdn.discordapp.com/attachments/945042450483920976/945450478899171408/IMG_3200.png")
    await ctx.send(embed=embed)


# reset a crashed game
@bot.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def reset(ctx):
    embed=discord.Embed()
    embed.add_field(name = 'RESET GAME:', value = 'In the event that a ranked/tournament game crashes or disconnects, players will recreate the game and continue playing from the point of the crash\n\n'
    'Here\'s a guide on how to proceed: https://discord.com/channels/628353660698624020/634046643330613248/947262817344585748')
    await ctx.send(embed=embed)


# datamined stats
@bot.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def datamine(ctx):
    embed=discord.Embed()
    embed.add_field(name = 'DATAMINED STATS:', value = 'We have uncovered many hidden stats in the game through datamining. See our full datamined stat spreadsheet here:\n'
    'https://docs.google.com/spreadsheets/d/16cEcCq-Gkudx5ESfqzS0MJlQI7WTvSIWsHVZS8jv750/edit?usp=sharing')
    await ctx.send(embed=embed)

# about rio stat files
@bot.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def stats(ctx):
    embed=discord.Embed()
    embed.add_field(name = 'RIO STATS:', value = 'By default, Project Rio records stats throughout a game and generates a stat json file to your compute.\n\n'
    'You can view these that files by opening the "StatFiles" folder in your Project Rio user directory (on Windows, this is likely in your Documents folder).')
    await ctx.send(embed=embed)

# chemistry link chart
@bot.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def chemistry(ctx):
    embed=discord.Embed()
    embed.add_field(name = 'CHARACTER CHEMISTRY CHART', value = 'The following image displays the chemistry links between all characters with a value of 0 being the worst and 100 being the best:\n')
    embed.set_image(url="https://media.discordapp.net/attachments/628354009865912350/815693119348932628/image0.png?width=678&height=676")
    await ctx.send(embed=embed)

# stadium boundary chart
@bot.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def stadium(ctx):
    embed=discord.Embed()
    embed.add_field(name = 'STADIUM BOUNDARY CHART', value = 'The following image displays the boundaries of all stadiums:\n')
    embed.set_image(url="https://media.discordapp.net/attachments/628354009865912350/943980502510104636/unknown.png")
    await ctx.send(embed=embed)



# displays server rules
@bot.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def rule(ctx, rule:int):
    embed=discord.Embed()
    if rule == 1:
        embed.add_field(name = "Hate Speech", value = "• Includes but is not limited to: racism, homophobia, transphobia, ableism, threats\n"
                                                      "• This includes profile pictures, usernames and custom statuses")
    elif rule == 2:
        embed.add_field(name="Posting NSFW Content", value="• This includes pictures, long text copy pastas, spam pinging, posting discord links, having sexual and or graphic conversations in voice or text channels, or other disruptive content.\n"
                                                           "• NSFW topics include but are not limited to: pornographic, excessively disturbing, sexually suggestive, or topics concerning past sexual experiences, sexual desires, gore, disturbing conversations about abuse, images of scantily clad people, images that make any allusion to sexual fetishes (vore, etc.), images of sex toys, or using trigger words.\n"
                                                           "• Extremely edgy content is content that is ‘excessively dark, often overbearingly depressive in nature could be considered humorous, or posts related to recent tragedies.\n"
                                                           "• This includes profile pictures, usernames and custom statuses.")
    elif rule == 3:
        embed.add_field(name = "Posting harmful or malicious links", value = "• This includes posting links to malicious websites.\n"
                                                          "• Any post that crashes or attempts to crash Discord or a user's computer.\n"
                                                          "• Any post that pretends to or does send malware to a user will be met with a ban, no questions asked.")
    elif rule == 4:
        embed.add_field(name = "Doxxing", value = "• Do not post personal details or identifying information of any users without that user's express permission.\n"
                                                  "• Do not post pictures of other people without their consent")
    elif rule == 5:
        embed.add_field(name="Spamming", value="• Keep discussions on topic to their respective channels\n"
                                               "• Messages in <#628353660698624024> must follow all other rules in the server\n"
                                               "• Self-promotion outside of the self-promotion channel is not permitted\n"
                                               "• Please only use Pings for their intended purpose. This includes @Netplayers and @New Netplayers for finding games in <#948321928760918087>")
    elif rule == 6:
        embed.add_field(name="Instigating Fights", value="• Intentional and continuous drama baiting/instigating is not allowed. Drama baiting/instigating is defined as constantly flaming/being toxic to users after being informally/formally warned.\n"
                                                         "• Members of the server must also be fair and understanding to those with different opinions.\n"
                                                         "• Mods or Admins may ask the discussion to end if it gets too heated.")
    elif rule == 7:
        embed.add_field(name='No "Crossing The Line"', value="• Please don't be too vitriolic, edgy, derogatory, or abrasive with your posts. Don’t be rude.\n"
                                                             "• Bullying and berating someone will not be tolerated. \n"
                                                             "• If you're unsure your communication is appropriate, then ask a moderator first.")
    elif rule == 8:
        embed.add_field(name="Having Non-English Conversations", value="• Please keep all text conversations in English. Most of the admins and mods in the server are native English speakers, so keeping conversations to English is most appreciated.\n"
                                                                       "• Non-English media is allowed, however it may be removed at the mods discretion if they think it might be breaking a rule in another language.")
    elif rule == 9:
        embed.add_field(name="Posting Excessively Loud Videos", value="• Excessively loud videos are not allowed in media channels.")

    elif rule == 10:
        embed.add_field(name="Asking for an ISO / ROM", value="• Asking for an ISO / ROM of any game is prohibited.\n"
                                                              "• Users must obtain these files on their own accord")
    elif rule == 11:
        embed.add_field(name="Netplay Specific Rules", value="• Users can only submit games to the ranked leaderboards from one account.  No smurfing.\n"
                                                             "• Dropping out of active tournaments will result in action from the moderation team depending on circumstances. Multiple offenses are more likely to result in bans from future tournaments.")
    elif rule == 12:
        embed.add_field(name="No politics", value="• Please refrain from bringing up controversial political opinions. This is a place to chat about Mario Baseball and other games.")
    await ctx.send(embed=embed)

# washed copypasta
@bot.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def washed(ctx):
    embed=discord.Embed()
    embed.add_field(name = "WASHED", value = "I would've won if i hadn't taken a break for a long time, scored more runs than you, played only top tier competition, didn't waste my time, gave up less runs than you, and I can beat remkey again anyway, and i did it for the people, and i only play top players so i don't know this matchup")
    await ctx.send(embed=embed)

# gamecube controller issues
@bot.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def gcc(ctx):
    embed=discord.Embed()
    embed.add_field(name = "Setting up a GameCube Controller",value = '''
To use a GameCube Controller with Rio, follow these steps:
- Install the proper drivers <https://wiki.dolphin-emu.org/index.php?title=How_to_use_the_Official_GameCube_Controller_Adapter_for_Wii_U_in_Dolphin#Avoid_vJoy>
- Change the controller port to "GameCube Adapter for WiiU" in the Controller settings
- If your adapter has a switch, set it to WiiU mode instead of PC mode
- Use port 1; only player 1 can control the menus in Mario Baseball
- Make sure no other Dolphin/Rio tabs are open at the same time. The controller can only connect to one window at a time
    ''')
    await ctx.send(embed=embed)

#Key given to bot through .env file so bot can run in server
bot.run(os.getenv('DISCORD_TOKEN'))
