import discord
import requests
from discord.ext import commands
from resources import ladders

BASE_GAMES_URL = "https://api.projectrio.app/games/"


class RecentGames(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(help="display a user's recent games")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def last(self, ctx, num_games: int = 10, user: str = "all", mode: str = "off"):
        if num_games > 50:
            num_games = 50
        web_mode = ladders.get_web_mode(mode)
        mode = ladders.find_game_mode(mode)
        api_url = BASE_GAMES_URL + "?limit_games=" + str(num_games) + "&tag=" + web_mode
        if user != "all":
            api_url += "&username=" + user

        games_data = requests.get(api_url).json()

        message = ""
        emojis = ctx.message.guild.emojis
        embed = discord.Embed(title=f"{mode} last {num_games} games for {user}")
        for index, game in enumerate(games_data["games"]):
            if game["Home User"].lower() == user.lower():
                user = game["Home User"]
                user_score = game["Home Score"]
                user_captain = next((e for e in emojis if e.name == game["Home Captain"].replace(" ", "")), "")
                opp_user = game["Away User"]
                opp_score = game["Away Score"]
                opp_captain = next((e for e in emojis if e.name == game["Away Captain"].replace(" ", "")), "")
            else:
                user = game["Away User"]
                user_score = game["Away Score"]
                user_captain = next((e for e in emojis if e.name == game["Away Captain"].replace(" ", "")), "")
                opp_user = game["Home User"]
                opp_score = game["Home Score"]
                opp_captain = next((e for e in emojis if e.name == game["Home Captain"].replace(" ", "")), "")
            timestamp = game["date_time_start"]
            if user_score > opp_score:
                message += f"<t:{timestamp}:d> {user_captain} **{user}** {user_score} - {opp_score} {opp_user} {opp_captain}\n"
            else:
                message += f"<t:{timestamp}:d> {user_captain} {user} {user_score} - {opp_score} **{opp_user}** {opp_captain}\n"

            if (index + 1) % 5 == 0:
                embed.add_field(name="", value=message, inline=False)
                message = ""

        embed.add_field(name="", value=message, inline=False)
        await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(RecentGames(client))
