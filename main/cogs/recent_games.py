import discord
from discord.ext import commands

from models.game import Game
from resources import ladders

BASE_GAMES_URL = "https://api.projectrio.app/games/"

stadium_map = {
    0: "Mario Stadium",
    1: "Bowser Castle",
    2: "Wario Palace",
    3: "Yoshi Park",
    4: "Peach Garden",
    5: "DK Jungle",
}


async def _format_game_line(game: Game, user: str, emojis, show_mode: bool) -> str:
    if game.home_user.lower() == user.lower():
        user = game.home_user
        user_score, opp_score = game.home_score, game.away_score
        user_captain = next((e for e in emojis if e.name.lower() == game.home_captain.replace(" ", "").lower()), "")
        opp_user = game.away_user
        opp_captain = next((e for e in emojis if e.name.lower() == game.away_captain.replace(" ", "").lower()), "")
    else:
        user = game.away_user
        user_score, opp_score = game.away_score, game.home_score
        user_captain = next((e for e in emojis if e.name.lower() == game.away_captain.replace(" ", "").lower()), "")
        opp_user = game.home_user
        opp_captain = next((e for e in emojis if e.name.lower() == game.home_captain.replace(" ", "").lower()), "")

    if user_score > opp_score:
        line = f"<t:{game.date_time_start}:d> {user_captain} **{user}** {user_score} - {opp_score} {opp_user} {opp_captain}"
    else:
        line = f"<t:{game.date_time_start}:d> {user_captain} {user} {user_score} - {opp_score} **{opp_user}** {opp_captain}"

    if game.innings_played != game.innings_selected:
        line += f" (F/{game.innings_played})"

    line += f" @ *{stadium_map[game.stadium]}*"
    if show_mode:
        line += f" ({await ladders.get_game_mode_name(game.game_mode)})"
    line += "\n"

    return line


async def _add_game_fields(embed: discord.Embed, games: list[Game], user: str, emojis, show_mode: bool):
    message = ""
    for index, game in enumerate(games):
        message += await _format_game_line(game, user, emojis, show_mode)
        if (index + 1) % 5 == 0:
            embed.add_field(name="", value=message, inline=False)
            message = ""
    embed.add_field(name="", value=message, inline=False)


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
        api_url = f"{BASE_GAMES_URL}?limit_games={num_games}"
        if mode != "all":
            api_url += f"&tag={web_mode}"
        if user != "all":
            api_url += f"&username={user}"

        async with self.client.session.get(api_url) as response:
            games_data = await response.json(content_type=None)
        games = [Game.model_validate(g) for g in games_data["games"]]

        embed = discord.Embed(title=f"{mode} last {len(games)} games for {user}")
        await _add_game_fields(embed, games, user, ctx.message.guild.emojis, show_mode=(mode == "all"))
        await ctx.send(embed=embed)

    @commands.command(help="display recent games between two users")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def h2h(self, ctx, user1: str, user2: str, mode: str = "all"):
        api_url = f"{BASE_GAMES_URL}?limit_games=30&username={user1}&vs_username={user2}"
        if mode != "all":
            api_url += f"&tag={ladders.get_web_mode(mode)}"

        async with self.client.session.get(api_url) as response:
            games_data = await response.json(content_type=None)
        games = [Game.model_validate(g) for g in games_data["games"]]

        embed = discord.Embed(title=f"Last {len(games)} games for {user1} vs {user2}")
        await _add_game_fields(embed, games, user1, ctx.message.guild.emojis, show_mode=True)
        await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(RecentGames(client))
