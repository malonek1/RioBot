import discord
from helpers.random_team_builder import random_teams_without_dupes
from models.matchmaking import MatchAnnouncement
from resources import EnvironmentVariables as ev
from resources import ladders
from services.randomness import flip_coin, random_hazards_stadium, random_quickplay_mode, random_stadium
from services.team_images import build_team_image_file


def build_match_message(ann: MatchAnnouncement) -> tuple[str, discord.Embed, discord.File | None]:
    """Build the (mentions, embed, file) for a found match.

    Returns ``file=None`` for non-randoms modes (no team image is generated).
    """
    game_type = ann.game_type
    player_a = ann.player_a
    player_b = ann.player_b
    mentions = f"<@{player_a.discord_id}> <@{player_b.discord_id}>"
    embed = discord.Embed()
    file: discord.File | None = None

    props = ladders.get_mode_rendering(game_type)

    if props.get("random_teams"):
        team_list = random_teams_without_dupes()
        captain_list = [team_list[0][0], team_list[1][0]]

        file = build_team_image_file(team_list, captain_list)
        embed.set_image(url="attachment://image.png")
        stadium = random_stadium()
        if flip_coin() == "Heads":
            away, home = player_a.name, player_b.name
        else:
            away, home = player_b.name, player_a.name

        teams_value = f"{away} (top team, away)\n{home} (bottom team, home)"
        if props.get("quickplay"):
            embed.add_field(name=f"{game_type} match found!", value=teams_value, inline=False)
            embed.add_field(name="Mode", value=random_quickplay_mode())
        else:
            embed.add_field(name=f"{game_type} match found!", value=teams_value)

        embed.add_field(name="Stadium", value=stadium)
    else:
        if flip_coin() == "Heads":
            slot_a, slot_b = "1p", "2p"
        else:
            slot_a, slot_b = "2p", "1p"
        if flip_coin() == "Heads":
            side_a, side_b = "away", "home"
        else:
            side_a, side_b = "home", "away"
        player_1 = f"{player_a.name} ({slot_a}, {side_a})"
        player_2 = f"{player_b.name} ({slot_b}, {side_b})"
        stadium = random_stadium()
        if props.get("hazards") and "Mario" in stadium:
            stadium = random_hazards_stadium()
        embed.add_field(name=f"{game_type} match found!",
                        value=f"{player_1} vs {player_2}\n\nFind matches in <#{ev.MM_BUTTON_CHANNEL_ID}>")
        embed.add_field(name="Stadium", value=stadium)

    return mentions, embed, file


def build_status_embed(queues: dict, recent_counts: dict) -> discord.Embed:
    """Build the persistent queue-status embed shown in the button channel."""
    details = ""
    total = 0
    rm_total = 0
    for m in ladders.GAME_MODES:
        total += len(queues[m])
        rm_total += recent_counts[m]
        details += f"{m}: {len(queues[m])}\n"

    embed = discord.Embed()
    embed.add_field(
        name=f"Press buttons below to search for a game.\n{total} player(s) in the matchmaking queue:",
        value=details)
    embed.set_footer(text=f"There have been {rm_total} matches made in the past hour!")
    return embed
