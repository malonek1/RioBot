import asyncio

import discord.ext.commands
from discord.ext import commands
import requests
import os

from dotenv import load_dotenv

from resources import EnvironmentVariables as ev

# Channel ID for #ranked-bot result submission channel
RANKED_BOT_CHANNEL_ID = int(ev.get_var("ranked_bot_channel_id"))
MOD_CHANNEL_ID = int(ev.get_var("mod_channel_id"))
MOD_ROLE_ID = int(ev.get_var("mod_role_id"))

class SubmitResults(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(help = "type !submit <winner username> <winner score> <loser score> <loser username> <\"Game Mode Name\" (in quotes)>)")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def submit(self, ctx: discord.ext.commands.Context, user1: str, score1: int, score2: int, user2: str, game_mode_name: str):
        load_dotenv()
        manual_submit_rio_key = os.getenv("RIO_KEY")

        check_emoji = "\U00002705"
        manual_submit_endpoint = "https://api.projectrio.app/manual_submit_game"

        if ctx.channel.id == RANKED_BOT_CHANNEL_ID:
            await ctx.message.add_reaction(check_emoji)
            # requests.post()

            def check_confirm(rxn, usr):
                return usr.name == "pokebunny" and (rxn.emoji == check_emoji)

            # Check for bot to see if a user confirmed or denied the results submitted by another user
            try:
                await self.client.wait_for('reaction_add', timeout=86400.0, check=check_confirm)
            except asyncio.TimeoutError:
                await ctx.send("Game was not accepted within 24 hours")
            else:
                manual_submit = {
                    "winner_username": user1,
                    "loser_username": user2,
                    "winner_score": score1,
                    "loser_score": score2,
                    "submitter_rio_key": manual_submit_rio_key,
                    "tag_set": game_mode_name,
                    "date": round(ctx.message.created_at.timestamp()),
                    "recalc": True
                }
                print(manual_submit)
                response = requests.post(manual_submit_endpoint, json=manual_submit)
                await ctx.send(f"Submitted: {user1} {score1} {score2} {user2} {game_mode_name}")
                # if response.status_code == 200:
                #     await ctx.send(f"Submitted: {user1} {score1} {score2} {user2} {game_mode_name}")
                # else:
                #     print(response.content)


    # Submit user command that allows a player to submit a game with another player
    # @commands.command(help = "type !submit <your score> <opponent score> @<your opponent>")
    # @commands.cooldown(1, 5, commands.BucketType.user)
    # async def submit(self, ctx, submitter_score: int, opp_score: int, opp_user: discord.Member):
    #     account_age = ctx.author.joined_at
    #     sysdate = dt.datetime.now(pytz.utc) - dt.timedelta(days=1)
    #     rb_channel = self.client.get_channel(RANKED_BOT_CHANNEL_ID)
    #     mod_channel = self.client.get_channel(MOD_CHANNEL_ID)
    #     if account_age < sysdate:
    #         if ctx.channel.id == RANKED_BOT_CHANNEL_ID:
    #             # Check to make sure that runs values input by user are between 0 and 99
    #             if (submitter_score < 0) or (opp_score < 0) or (submitter_score > 99) or (opp_score > 99):
    #                 embed = discord.Embed(title='Scores must be between 0 and 100!', color=0xEA7D07)
    #                 await ctx.send(embed=embed)
    #             else:
    #                 # Initial bot message displayed for game submitted by primary user
    #                 submitter_user = ctx.author
    #                 if submitter_user == opp_user:
    #                     embed = discord.Embed(title='You cannot submit a game against yourself!', color=0xEA7D07)
    #                     await ctx.send(embed=embed)
    #                 else:
    #                     embed = discord.Embed(
    #                         title='Are you submitting to the Stars-Off leaderboards or the Stars-On leaderboards?',
    #                         color=0xC496EF)
    #                     embed.add_field(name='STARS-OFF', value=':goat:', inline=True)
    #                     embed.add_field(name='STARS-ON', value=':star:', inline=True)
    #                     game_mode_message = await ctx.send(embed=embed)
    #                     star_emoji = "\U00002B50"
    #                     goat_emoji = "\U0001F410"
    #                     await game_mode_message.add_reaction(goat_emoji)
    #                     await game_mode_message.add_reaction(star_emoji)
    #
    #                     def check_star(rxn, usr):
    #                         return usr == submitter_user and (str(rxn.emoji) in [star_emoji, goat_emoji])
    #
    #                     try:
    #                         reaction, user = await self.client.wait_for('reaction_add', timeout=300.0, check=check_star)
    #                     except asyncio.TimeoutError:
    #                         # If user doesn't react to message within 1 minute, initial message is deleted
    #                         await game_mode_message.delete()
    #                         embed = discord.Embed(
    #                             title=f'Cancelled match between {submitter_user.name} and {opp_user.name} for not reacting in time!',
    #                             color=0xFF5733)
    #                         await ctx.send(embed=embed)
    #                     else:
    #                         if reaction.emoji == star_emoji or reaction.emoji == goat_emoji:
    #                             if reaction.emoji == goat_emoji:
    #                                 mode = 'OFF', ':goat:'
    #                             else:
    #                                 mode = 'ON', ':star:'
    #                             embed = discord.Embed(
    #                                 title=f'{opp_user.name}, confirm the results of your Stars-{mode[0]} {mode[1]} '
    #                                       f'game by reacting with :white_check_mark: or reject the results with :x: ',
    #                                 color=0xC496EF)
    #                             embed.add_field(name=f'{submitter_user.name} score:', value=submitter_score, inline=True)
    #                             embed.add_field(name=f'{opp_user.name} score:', value=opp_score, inline=True)
    #                             confirm_message = await ctx.send(embed=embed)
    #                             check_emoji = "\U00002705"
    #                             ex_emoji = "\U0000274C"
    #                             await confirm_message.add_reaction(check_emoji)
    #                             await confirm_message.add_reaction(ex_emoji)
    #
    #                             # Check for bot to see if a user confirmed or denied the results submitted by another user
    #                             def check_confirm(rxn, usr):
    #                                 if usr == opp_user and (
    #                                         str(rxn.emoji) in [check_emoji, ex_emoji]):
    #                                     return usr == opp_user and (str(rxn.emoji) in [check_emoji, ex_emoji])
    #                                 elif usr == submitter_user and (str(rxn.emoji) in [ex_emoji]):
    #                                     return usr == submitter_user and (str(rxn.emoji) in [ex_emoji])
    #
    #                             try:
    #                                 reaction, user = await self.client.wait_for('reaction_add', timeout=300.0,
    #                                                                             check=check_confirm)
    #                             except asyncio.TimeoutError:
    #                                 # If user doesn't react to message within 5 minutes, initial message is deleted
    #                                 await game_mode_message.delete()
    #                                 await confirm_message.delete()
    #                                 embed = discord.Embed(
    #                                     title=f'Cancelled Stars-{mode[0]} match between {submitter_user.name} and {opp_user.name} for not reacting in time!',
    #                                     color=0xFF5733)
    #                                 await ctx.send(embed=embed)
    #                             else:
    #                                 # Confirmation message displays if secondary user reacts with check mark
    #                                 if reaction.emoji == check_emoji:
    #                                     await game_mode_message.delete()
    #                                     await confirm_message.delete()
    #                                     embed = discord.Embed(
    #                                         title=f'Confirmed Stars-{mode[0]} match between {submitter_user.name} and {opp_user.name}!',
    #                                         color=0x138F13)
    #                                     await ctx.send(embed=embed)
    #
    #                                     # Update Spreadsheet
    #                                     if submitter_score > opp_score:
    #                                         print('Submitter Wins!')
    #                                         SheetsParser.confirm_match(f'{submitter_user.name}', f'{opp_user.name}',
    #                                                                    f'{submitter_user.id}', f'{opp_user.id}',
    #                                                                    submitter_score,
    #                                                                    opp_score, mode[0])
    #                                     elif submitter_score < opp_score:
    #                                         print('Opponent Wins!')
    #                                         SheetsParser.confirm_match(f'{opp_user.name}', f'{submitter_user.name}',
    #                                                                    f'{opp_user.id}', f'{submitter_user.id}', opp_score,
    #                                                                    submitter_score, mode[0])
    #                                 # Rejection message displays if secondary user reacts with an X mark
    #                                 elif reaction.emoji == ex_emoji:
    #                                     await game_mode_message.delete()
    #                                     await confirm_message.delete()
    #                                     embed = discord.Embed(
    #                                         title=f'Cancelled Stars-{mode[0]} match between {submitter_user.name} and {opp_user.name}!',
    #                                         color=0xFF5733)
    #                                     await ctx.send(embed=embed)
    #
    #         else:
    #             embed = discord.Embed(color=0xEA7D07)
    #             embed.add_field(name='The !submit command must be used here:', value='<#947699610921599006>')
    #             await ctx.send(embed=embed)
    #     else:
    #         print("User " + str(ctx.author.name) + " tried submitting a game with an invalid discord account age of " + str(account_age))
    #         rb_embed = discord.Embed(
    #             title=f"User {ctx.author.name} hasn't been in the server long enough to submit games!",
    #             color=0xFF5733)
    #
    #         mod_embed = discord.Embed(
    #             title=f'Suspicious activity detected!',
    #             color=0xFF5733)
    #         mod_embed.add_field(name=f'Discord User Name:', value=str(ctx.author.name), inline=False)
    #         mod_embed.add_field(name=f'Discord User ID:', value=str(ctx.author.id), inline=False)
    #         mod_embed.add_field(name=f'Joined Server:', value=account_age, inline=False)
    #         mod_embed.add_field(name=f'Channel Activity:', value=f'<#{RANKED_BOT_CHANNEL_ID}>', inline=False)
    #         await rb_channel.send(embed=rb_embed)
    #         await mod_channel.send(f'<@&{MOD_ROLE_ID}>', embed=mod_embed)
    # @commands.command(help = "moderator tool to manually submit games")
    # @commands.has_any_role("Admins", "Moderator", "Bot Developer")
    # async def forceSubmit(self, ctx, first_score: int, second_score: int, first_user: discord.Member,
    #                       second_user: discord.Member):
    #     if ctx.channel.id == RANKED_BOT_CHANNEL_ID:
    #         # Check to make sure that runs values input by user are between 0 and 99
    #         if (first_score < 0) or (second_score < 0) or (first_score > 99) or (second_score > 99):
    #             embed = discord.Embed(title='Scores must be between 0 and 100!', color=0xEA7D07)
    #             await ctx.send(embed=embed)
    #         else:
    #             embed = discord.Embed(
    #                 title='Are you submitting to the Stars-Off leaderboards or the Stars-On leaderboards?',
    #                 color=0xC496EF)
    #             embed.add_field(name='STARS-OFF', value=':goat:', inline=True)
    #             embed.add_field(name='STARS-ON', value=':star:', inline=True)
    #             game_mode_message = await ctx.send(embed=embed)
    #             star_emoji = "\U00002B50"
    #             goat_emoji = "\U0001F410"
    #             await game_mode_message.add_reaction(goat_emoji)
    #             await game_mode_message.add_reaction(star_emoji)
    #
    #             def check_star(rxn, usr):
    #                 return usr == ctx.author and (str(rxn.emoji) in [star_emoji, goat_emoji])
    #
    #             try:
    #                 reaction, user = await self.client.wait_for('reaction_add', timeout=300.0, check=check_star)
    #             except asyncio.TimeoutError:
    #                 # If user doesn't react to message within 5 minutes, initial message is deleted
    #                 await game_mode_message.delete()
    #                 embed = discord.Embed(
    #                     title=f'Cancelled match between {first_user.name} and {second_user.name} for not reacting in time!',
    #                     color=0xFF5733)
    #                 await ctx.send(embed=embed)
    #
    #             else:
    #                 if reaction.emoji == star_emoji or reaction.emoji == goat_emoji:
    #                     mode = 'OFF' if reaction.emoji == goat_emoji else 'ON'
    #                     await game_mode_message.delete()
    #                     embed = discord.Embed(
    #                         title=f'Confirmed Stars-{mode} match between {second_user.name} and {first_user.name}!',
    #                         color=0x138F13)
    #                     await ctx.send(embed=embed)
    #                     if first_score > second_score:
    #                         print('Submitter Wins!')
    #                         SheetsParser.confirm_match(f'{first_user.name}', f'{second_user.name}', f'{first_user.id}',
    #                                                    f'{second_user.id}', first_score, second_score, mode)
    #                     elif first_score < second_score:
    #                         print('Opponent Wins!')
    #                         SheetsParser.confirm_match(f'{second_user.name}', f'{first_user.name}', f'{second_user.id}',
    #                                                    f'{first_user.id}', second_score, first_score, mode)
    #
    #     else:
    #         embed = discord.Embed(color=0xEA7D07)
    #         embed.add_field(name='The !submit command must be used here:', value='<#947699610921599006>')
    #         await ctx.send(embed=embed)
    #

async def setup(client):
    await client.add_cog(SubmitResults(client))
