import discord
from discord.ext import commands
from resources import ladders
from resources.api import GAMES_URL
from models.game import Game

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
    async def last(self, ctx, num_games: int = 10, user: str = "all", mode: str = "all"):
        if num_games > 40:
            num_games = 40
        web_mode = ladders.get_web_mode(mode)
        mode = ladders.find_game_mode(mode)
        api_url = f"{GAMES_URL}?limit_games={num_games}"
        if mode != "all":
            api_url += f"&tag={web_mode}"
        if user != "all":
            api_url += f"&username={user}"

        async with self.client.session.get(api_url) as response:
            games_data = await response.json(content_type=None)
        games = [Game.model_validate(g) for g in games_data["games"]]

        message = ""
        emojis = ctx.message.guild.emojis
        embed = discord.Embed(title=f"{mode} last {len(games)} games for {user}")
        for index, game in enumerate(games):
            if game.home_user.lower() == user.lower():
                user = game.home_user
                user_score = game.home_score
                user_captain = next((e for e in emojis if e.name.lower() == game.home_captain.replace(" ", "").lower()), "")
                opp_user = game.away_user
                opp_score = game.away_score
                opp_captain = next((e for e in emojis if e.name.lower() == game.away_captain.replace(" ", "").lower()), "")
            else:
                user = game.away_user
                user_score = game.away_score
                user_captain = next((e for e in emojis if e.name.lower() == game.away_captain.replace(" ", "").lower()), "")
                opp_user = game.home_user
                opp_score = game.home_score
                opp_captain = next((e for e in emojis if e.name.lower() == game.home_captain.replace(" ", "").lower()), "")
            if user_score > opp_score:
                message += f"<t:{game.date_time_start}:d> {user_captain} **{user}** {user_score} - {opp_score} {opp_user} {opp_captain}"
            else:
                message += f"<t:{game.date_time_start}:d> {user_captain} {user} {user_score} - {opp_score} **{opp_user}** {opp_captain}"
            if game.innings_played != game.innings_selected:
                message += " (F/" + str(game.innings_played) + ")"
            stadium = stadium_map[game.stadium]
            message += f" @ *{stadium}*\n"
            if mode == "all":
                message += f" ({await ladders.get_game_mode_name(game.game_mode)})\n"

            if (index + 1) % 5 == 0:
                embed.add_field(name="", value=message, inline=False)
                message = ""

        embed.add_field(name="", value=message, inline=False)
        await ctx.send(embed=embed)

    # TODO: Reuse code between h2h/last
    @commands.command(help="display recent games between two users")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def h2h(self, ctx, user1: str, user2: str, mode: str = "all"):
        num_games = 30
        api_url = f"{GAMES_URL}?limit_games={str(num_games)}&username={user1}&vs_username={user2}"
        if mode != "all":
            web_mode = ladders.get_web_mode(mode)
            api_url += f"&tag={web_mode}"

        async with self.client.session.get(api_url) as response:
            games_data = await response.json(content_type=None)
        games = [Game.model_validate(g) for g in games_data["games"]]

        message = ""
        emojis = ctx.message.guild.emojis
        embed = discord.Embed(title=f"Last {len(games)} games for {user1} vs {user2}")
        for index, game in enumerate(games):
            if game.home_user.lower() == user1.lower():
                user1 = game.home_user
                user_score = game.home_score
                user_captain = next(
                    (e for e in emojis if e.name.lower() == game.home_captain.replace(" ", "").lower()), "")
                opp_user = game.away_user
                opp_score = game.away_score
                opp_captain = next(
                    (e for e in emojis if e.name.lower() == game.away_captain.replace(" ", "").lower()), "")
            else:
                user1 = game.away_user
                user_score = game.away_score
                user_captain = next(
                    (e for e in emojis if e.name.lower() == game.away_captain.replace(" ", "").lower()), "")
                opp_user = game.home_user
                opp_score = game.home_score
                opp_captain = next(
                    (e for e in emojis if e.name.lower() == game.home_captain.replace(" ", "").lower()), "")
            if user_score > opp_score:
                message += f"<t:{game.date_time_start}:d> {user_captain} **{user1}** {user_score} - {opp_score} {opp_user} {opp_captain}"
            else:
                message += f"<t:{game.date_time_start}:d> {user_captain} {user1} {user_score} - {opp_score} **{opp_user}** {opp_captain}"
            if game.innings_played != game.innings_selected:
                message += " (F/" + str(game.innings_played) + ")"
            stadium = stadium_map[game.stadium]
            message += f" @ *{stadium}*"
            message += f" ({await ladders.get_game_mode_name(game.game_mode)})\n"

            if (index + 1) % 5 == 0:
                embed.add_field(name="", value=message, inline=False)
                message = ""

        embed.add_field(name="", value=message, inline=False)
        await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(RecentGames(client))
