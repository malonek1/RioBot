import discord
import requests
from discord.ext import commands
from resources import ladders

BASE_GAMES_URL = "https://api.projectrio.app/games/"

stadium_map = {
    0: "Mario Stadium",
    1: "Bowser Castle",
    2: "Wario Palace",
    3: "Yoshi Park",
    4: "Peach Garden",
    5: "DK Jungle"
}


class RecentGames(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(help="display a user's recent games")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def last(self, ctx, num_games: int = 10, user: str = "all", mode: str = "off"):
        if num_games > 40:
            num_games = 40
        web_mode = ladders.get_web_mode(mode)
        mode = ladders.find_game_mode(mode)
        api_url = f"{BASE_GAMES_URL}?limit_games={num_games}&tag={web_mode}"
        if user != "all":
            api_url += f"&username={user}"

        games_data = requests.get(api_url).json()

        message = ""
        emojis = ctx.message.guild.emojis
        embed = discord.Embed(title=f"{mode} last {len(games_data['games'])} games for {user}")
        for index, game in enumerate(games_data["games"]):
            if game["home_user"].lower() == user.lower():
                user = game["home_user"]
                user_score = game["home_score"]
                user_captain = next((e for e in emojis if e.name.lower() == game["home_captain"].replace(" ", "").lower()), "")
                opp_user = game["away_user"]
                opp_score = game["away_score"]
                opp_captain = next((e for e in emojis if e.name.lower() == game["away_captain"].replace(" ", "").lower()), "")
            else:
                user = game["away_user"]
                user_score = game["away_score"]
                user_captain = next((e for e in emojis if e.name.lower() == game["away_captain"].replace(" ", "").lower()), "")
                opp_user = game["home_user"]
                opp_score = game["home_score"]
                opp_captain = next((e for e in emojis if e.name.lower() == game["home_captain"].replace(" ", "").lower()), "")
            timestamp = game["date_time_start"]
            if user_score > opp_score:
                message += f"<t:{timestamp}:d> {user_captain} **{user}** {user_score} - {opp_score} {opp_user} {opp_captain}"
            else:
                message += f"<t:{timestamp}:d> {user_captain} {user} {user_score} - {opp_score} **{opp_user}** {opp_captain}"
            if game["innings_played"] != game["innings_selected"]:
                message += " (F/" + str(game["innings_played"]) + ")"
            stadium = stadium_map[game["stadium"]]
            message += f" @ *{stadium}*\n"

            if (index + 1) % 5 == 0:
                embed.add_field(name="", value=message, inline=False)
                message = ""

        embed.add_field(name="", value=message, inline=False)
        await ctx.send(embed=embed)

    # TODO: Reuse code between h2h/last
    @commands.command(help="display recent games between two users")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def h2h(self, ctx, user1: str, user2: str, num_games: int = 10):
        api_url = f"{BASE_GAMES_URL}?limit_games={str(num_games)}&username={user1}&vs_username={user2}"

        games_data = requests.get(api_url).json()

        message = ""
        emojis = ctx.message.guild.emojis
        embed = discord.Embed(title=f"Last {len(games_data['games'])} games for {user1} vs {user2}")
        for index, game in enumerate(games_data["games"]):
            if game["home_user"].lower() == user1.lower():
                user1 = game["home_user"]
                user_score = game["home_score"]
                user_captain = next(
                    (e for e in emojis if e.name.lower() == game["home_captain"].replace(" ", "").lower()), "")
                opp_user = game["away_user"]
                opp_score = game["away_score"]
                opp_captain = next(
                    (e for e in emojis if e.name.lower() == game["away_captain"].replace(" ", "").lower()), "")
            else:
                user1 = game["away_user"]
                user_score = game["away_score"]
                user_captain = next(
                    (e for e in emojis if e.name.lower() == game["away_captain"].replace(" ", "").lower()), "")
                opp_user = game["home_user"]
                opp_score = game["home_score"]
                opp_captain = next(
                    (e for e in emojis if e.name.lower() == game["home_captain"].replace(" ", "").lower()), "")
            timestamp = game["date_time_start"]
            if user_score > opp_score:
                message += f"<t:{timestamp}:d> {user_captain} **{user1}** {user_score} - {opp_score} {opp_user} {opp_captain}"
            else:
                message += f"<t:{timestamp}:d> {user_captain} {user1} {user_score} - {opp_score} **{opp_user}** {opp_captain}"
            if game["innings_played"] != game["innings_selected"]:
                message += " (F/" + str(game["innings_played"]) + ")"
            stadium = stadium_map[game["stadium"]]
            message += f" @ *{stadium}*"
            message += f" ({ladders.get_game_mode_name(game['game_mode'])})\n"

            if (index + 1) % 5 == 0:
                embed.add_field(name="", value=message, inline=False)
                message = ""

        embed.add_field(name="", value=message, inline=False)
        await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(RecentGames(client))
