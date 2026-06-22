import discord

from resources import EnvironmentVariables as ev, ladders
from services.random_functions import rfRandomTeamsWithoutDupes, rfRandomStadium, rfFlipCoin, rfRandomHazardsStadium, \
    rfRandomQuickplayMode
from services.image_functions import ifBuildTeamImageFile
from models.matchmaking import MatchAnnouncement


def build_match_message(ann: MatchAnnouncement) -> tuple[str, discord.Embed, discord.File | None]:
    """Build the (mentions, embed, file) for a found match.

    Returns ``file=None`` for non-randoms modes (no team image is generated).
    """
    game_type = ann.game_type
    searcher = ann.searcher
    opponent = ann.opponent
    mentions = f"<@{searcher.discord_id}> <@{opponent.discord_id}>"
    embed = discord.Embed()
    file: discord.File | None = None

    if "Random" in game_type or "Quickplay" in game_type or "Balla" in game_type:
        team_list = rfRandomTeamsWithoutDupes()
        captain_list = [team_list[0][0], team_list[1][0]]

        file = ifBuildTeamImageFile(team_list, captain_list)
        embed.set_image(url="attachment://image.png")
        stadium = rfRandomStadium()
        if rfFlipCoin() == "Heads":
            away = searcher.name
            home = opponent.name
        else:
            away = opponent.name
            home = searcher.name

        if "Quickplay" in game_type:
            embed.add_field(name=game_type + " match found!",
                            value=away + " (top team, away)\n" + home + " (bottom team, home)", inline=False)
            embed.add_field(name="Mode", value=rfRandomQuickplayMode())
        else:
            embed.add_field(name=game_type + " match found!",
                            value=away + " (top team, away)\n" + home + " (bottom team, home)")

        embed.add_field(name="Stadium", value=stadium)
    else:
        player_1 = searcher.name + " ("
        player_2 = opponent.name + " ("
        if rfFlipCoin() == "Heads":
            player_1 += "1p, "
            player_2 += "2p, "
        else:
            player_1 += "2p, "
            player_2 += "1p, "
        if rfFlipCoin() == "Heads":
            player_1 += "away)"
            player_2 += "home)"
        else:
            player_1 += "home)"
            player_2 += "away)"
        stadium = rfRandomStadium()
        if "Hazards" in game_type and "Mario" in stadium:
            stadium = rfRandomHazardsStadium()
        embed.add_field(name=game_type + " match found!",
                        value=player_1 + " vs " + player_2 + "\n\nFind matches in <#" + str(
                            ev.MM_BUTTON_CHANNEL_ID) + ">")
        embed.add_field(name="Stadium", value=stadium)

    return mentions, embed, file


def build_status_embed(queues: dict, recent_matches: dict) -> discord.Embed:
    """Build the persistent queue-status embed shown in the button channel."""
    details = ""
    total = 0
    rm_total = 0
    for m in ladders.GAME_MODES:
        total += len(queues[m])
        rm_total += len(recent_matches[m])
        details += m + ": " + str(len(queues[m])) + "\n"

    embed = discord.Embed()
    embed.add_field(
        name="Press buttons below to search for a game.\n" + str(total) + " player(s) in the matchmaking queue:",
        value=details)
    embed.set_footer(text="There have been " + str(rm_total) + " matches made in the past hour!")
    return embed
