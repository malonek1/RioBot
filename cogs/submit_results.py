import asyncio

import discord
from discord.ext import commands
import datetime as dt
import pytz
import requests

from resources import SheetsParser
from resources import EnvironmentVariables as ev
from resources import ladders

# Channel ID for #ranked-bot result submission channel
RANKED_BOT_CHANNEL_ID = int(ev.get_var("ranked_bot_channel_id"))
MOD_CHANNEL_ID = int(ev.get_var("mod_channel_id"))
MOD_ROLE_ID = int(ev.get_var("mod_role_id"))

WEB_SUBMIT_URL = "https://api.projectrio.app/submit_game"


class SubmitResults(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Submit user command that allows a player to submit a game with another player
    @commands.command(help="type !submit <game_id> <user1> <score1> <user2> <score2>")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def submit(self, ctx, game_id: int, user1: str, score1: int, user2: str, score2: int):
        account_age = ctx.author.joined_at
        sysdate = dt.datetime.now(pytz.utc) - dt.timedelta(days=1)
        rb_channel = self.client.get_channel(RANKED_BOT_CHANNEL_ID)
        mod_channel = self.client.get_channel(MOD_CHANNEL_ID)
        if account_age < sysdate:
            if ctx.channel.id == RANKED_BOT_CHANNEL_ID:

                # Check to make sure that runs values input by user are between 0 and 99
                if score1 < 0 or score2 < 0 or score1 > 99 or score2 > 99:
                    embed = discord.Embed(title='Scores must be between 0 and 100!', color=0xEA7D07)
                    await ctx.send(embed=embed)
                else:
                    # Initial bot message displayed for game submitted by primary user
                    if user1 == user2:
                        embed = discord.Embed(title='You cannot submit a game against yourself!', color=0xEA7D07)
                        await ctx.send(embed=embed)
                    else:
                        submitter_user = ctx.author
                        embed = discord.Embed(
                            title='What game mode are you submitting for?',
                            color=0xC496EF)
                        embed.add_field(name=ladders.STARS_OFF_MODE, value=':goat:', inline=True)
                        embed.add_field(name=ladders.STARS_ON_MODE, value=':star:', inline=True)
                        embed.add_field(name=ladders.BIG_BALLA_MODE, value=':basketball:', inline=True)
                        game_mode_message = await ctx.send(embed=embed)
                        star_emoji = "\U00002B50"
                        goat_emoji = "\U0001F410"
                        ball_emoji = "\U0001F3C0"
                        emojis = [star_emoji, goat_emoji, ball_emoji]
                        await game_mode_message.add_reaction(goat_emoji)
                        await game_mode_message.add_reaction(star_emoji)
                        await game_mode_message.add_reaction(ball_emoji)

                        def check_star(rxn, usr):
                            return usr == submitter_user and (str(rxn.emoji) in emojis)

                        try:
                            reaction, user = await self.client.wait_for('reaction_add', timeout=300.0, check=check_star)
                        except asyncio.TimeoutError:
                            # If user doesn't react to message within 1 minute, initial message is deleted
                            await game_mode_message.delete()
                            embed = discord.Embed(
                                title=f'Cancelled match between {user1} and {user2} for not reacting in time!',
                                color=0xFF5733)
                            await ctx.send(embed=embed)
                        else:
                            if reaction.emoji in emojis:
                                if reaction.emoji == goat_emoji:
                                    mode = ladders.STARS_OFF_MODE, ':goat:'
                                elif reaction.emoji == ball_emoji:
                                    mode = ladders.BIG_BALLA_MODE, ':basketball:'
                                else:
                                    mode = ladders.STARS_ON_MODE, ':star:'

                                await game_mode_message.delete()
                                embed = discord.Embed(
                                    title=f'Submitted {mode[0]} match between {user1} and {user2}!',
                                    color=0x138F13)
                                if score1 > score2:
                                    winner_user = user1
                                    winner_score = score1
                                    loser_user = user2
                                    loser_score = score2
                                else:
                                    winner_user = user2
                                    winner_score = score2
                                    loser_user = user1
                                    loser_score = score2
                                post_body = {
                                    "GameID": game_id,
                                    "Winner Username": winner_user,
                                    "Winner Score": winner_score,
                                    "Loser Username": loser_user,
                                    "Loser Score": loser_score,
                                    "TagSet": mode[0]
                                }
                                print(post_body)
                                response = requests.post(WEB_SUBMIT_URL, json=post_body)
                                print(response.status_code)
                                print(response.json())
                                await ctx.send(embed=embed)

            else:
                embed = discord.Embed(color=0xEA7D07)
                embed.add_field(name='The !submit command must be used here:',
                                value=f'<#{ev.get_var("ranked_bot_channel_id")}>')
                await ctx.send(embed=embed)
        else:
            print("User " + str(
                ctx.author.name) + " tried submitting a game with an invalid discord account age of " + str(
                account_age))
            rb_embed = discord.Embed(
                title=f"User {ctx.author.name} hasn't been in the server long enough to submit games!",
                color=0xFF5733)

            mod_embed = discord.Embed(
                title=f'Suspicious activity detected!',
                color=0xFF5733)
            mod_embed.add_field(name=f'Discord User Name:', value=str(ctx.author.name), inline=False)
            mod_embed.add_field(name=f'Discord User ID:', value=str(ctx.author.id), inline=False)
            mod_embed.add_field(name=f'Joined Server:', value=account_age, inline=False)
            mod_embed.add_field(name=f'Channel Activity:', value=f'<#{RANKED_BOT_CHANNEL_ID}>', inline=False)
            await rb_channel.send(embed=rb_embed)
            await mod_channel.send(f'<@&{MOD_ROLE_ID}>', embed=mod_embed)

    @commands.command(help="moderator tool to manually submit games")
    @commands.has_any_role("Admins", "Moderator", "Bot Developer")
    async def forceSubmit(self, ctx, first_score: int, second_score: int, first_user: discord.Member,
                          second_user: discord.Member):
        if ctx.channel.id == RANKED_BOT_CHANNEL_ID:
            # Check to make sure that runs values input by user are between 0 and 99
            if (first_score < 0) or (second_score < 0) or (first_score > 99) or (second_score > 99):
                embed = discord.Embed(title='Scores must be between 0 and 100!', color=0xEA7D07)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title='Are you submitting to the Stars-Off leaderboards or the Stars-On leaderboards?',
                    color=0xC496EF)
                embed.add_field(name='STARS-OFF', value=':goat:', inline=True)
                embed.add_field(name='STARS-ON', value=':star:', inline=True)
                game_mode_message = await ctx.send(embed=embed)
                star_emoji = "\U00002B50"
                goat_emoji = "\U0001F410"
                await game_mode_message.add_reaction(goat_emoji)
                await game_mode_message.add_reaction(star_emoji)

                def check_star(rxn, usr):
                    return usr == ctx.author and (str(rxn.emoji) in [star_emoji, goat_emoji])

                try:
                    reaction, user = await self.client.wait_for('reaction_add', timeout=300.0, check=check_star)
                except asyncio.TimeoutError:
                    # If user doesn't react to message within 5 minutes, initial message is deleted
                    await game_mode_message.delete()
                    embed = discord.Embed(
                        title=f'Cancelled match between {first_user.name} and {second_user.name} for not reacting in time!',
                        color=0xFF5733)
                    await ctx.send(embed=embed)

                else:
                    if reaction.emoji == star_emoji or reaction.emoji == goat_emoji:
                        mode = 'OFF' if reaction.emoji == goat_emoji else 'ON'
                        await game_mode_message.delete()
                        embed = discord.Embed(
                            title=f'Confirmed Stars-{mode} match between {second_user.name} and {first_user.name}!',
                            color=0x138F13)
                        await ctx.send(embed=embed)
                        if first_score > second_score:
                            print('Submitter Wins!')
                            SheetsParser.confirm_match(f'{first_user.name}', f'{second_user.name}', f'{first_user.id}',
                                                       f'{second_user.id}', first_score, second_score, mode)
                        elif first_score < second_score:
                            print('Opponent Wins!')
                            SheetsParser.confirm_match(f'{second_user.name}', f'{first_user.name}', f'{second_user.id}',
                                                       f'{first_user.id}', second_score, first_score, mode)

        else:
            embed = discord.Embed(color=0xEA7D07)
            embed.add_field(name='The !submit command must be used here:', value='<#947699610921599006>')
            await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(SubmitResults(client))
