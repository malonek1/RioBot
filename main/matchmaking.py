import asyncio
import logging
import time

import discord
from discord.ext import commands

from resources import EnvironmentVariables as ev, ladders, rio_name_map
from models.matchmaking import QueuedPlayer, MatchAnnouncement
from services.matchmaking_embeds import build_match_message, build_status_embed

logger = logging.getLogger(__name__)

# --- Tunable constants -------------------------------------------------------
# Starting percentile range for matchmaking search.
BASE_PERCENTILE_RANGE = 0.5
# Divisor controlling how quickly the search range widens with time in queue.
SEARCH_WIDEN_INTERVAL = 120
# Default rating assigned to players who aren't on the ladder yet.
DEFAULT_RATING = 1300
# How long a match is counted toward the "matches in the past hour" stat.
RECENT_MATCH_WINDOW = 3600
# Seconds a player must wait before a role ping goes out for them.
PING_AFTER = 120
# Minimum gap between role pings for the same role.
PING_COOLDOWN = 1800
# Seconds before a player gets an AFK reminder DM.
AFK_AFTER = 1800

# --- Channel / role configuration -------------------------------------------
BUTTON_CHANNEL_ID = ev.MM_BUTTON_CHANNEL_ID
MATCH_CHANNEL_ID = ev.MM_MATCH_CHANNEL_ID
BOT_SPAM_CHANNEL_ID = ev.BOT_SPAM_CHANNEL_ID

STARS_OFF_ROLE = f"<@&{ev.MM_STARS_OFF_ROLE_ID}>"
STARS_ON_ROLE = f"<@&{ev.MM_STARS_ON_ROLE_ID}>"


class Matchmaker:
    """Owns all matchmaking state and serializes mutations behind a lock.

    The golden rule: *decide under the lock, do Discord I/O after releasing it*.
    Every read-modify of the queues happens inside ``self._lock`` and never
    awaits a network call, which is what makes the previous
    "dict changed size during iteration" / double-match races impossible.

    This class is pure engine — it holds no buttons or task loops. The
    Matchmaking cog (cogs/matchmaking.py) owns the Discord lifecycle and drives
    it via ``add_player`` / ``remove_player`` / ``run_refresh``.
    """

    def __init__(self):
        self._lock = asyncio.Lock()
        self.queues: dict[str, dict[str, QueuedPlayer]] = {m: {} for m in ladders.GAME_MODES}
        self.match_count: dict[str, int] = {m: 1 for m in ladders.GAME_MODES}
        self.recent_matches: dict[str, list[float]] = {m: [] for m in ladders.GAME_MODES}
        self.last_ping_time: dict[str, float] = {STARS_OFF_ROLE: 0.0, STARS_ON_ROLE: 0.0}
        self.mm_message: discord.Message | None = None

    # --- Queue mutation (lock-protected) ------------------------------------
    def _remove_from_all(self, player_id: str):
        for m in ladders.GAME_MODES:
            self.queues[m].pop(player_id, None)

    def _find_match(self, game_type: str, user_id: str, min_rating: float, max_rating: float) -> str | None:
        """Return the id of the closest-rated opponent in range, or None."""
        mode_queue = self.queues[game_type]
        if len(mode_queue) < 2:
            return None
        me = mode_queue[user_id]
        best_id: str | None = None
        best_diff: float | None = None
        for pid, player in mode_queue.items():
            if pid == user_id:
                continue
            if min_rating <= player.rating <= max_rating:
                diff = abs(player.rating - me.rating)
                if best_diff is None or diff < best_diff:
                    best_id = pid
                    best_diff = diff
        return best_id

    def _commit_match(self, game_type: str, user_id: str, opponent_id: str) -> MatchAnnouncement:
        """Remove both players from every queue and record the match. Lock held."""
        searcher = self.queues[game_type][user_id]
        opponent = self.queues[game_type][opponent_id]
        self._remove_from_all(user_id)
        self._remove_from_all(opponent_id)
        number = self.match_count[game_type]
        self.match_count[game_type] += 1
        self.recent_matches[game_type].append(time.time())
        return MatchAnnouncement(game_type=game_type, number=number, searcher=searcher, opponent=opponent)

    @staticmethod
    def _role_for_mode(game_type: str) -> tuple[str, str]:
        if game_type in (ladders.STARS_ON_MODE, ladders.BIG_BALLA):
            return STARS_ON_ROLE, "STARS-ON"
        # Stars-off, hazards, randoms and anything else default to stars-off.
        return STARS_OFF_ROLE, "STARS-OFF"

    # --- Search range -------------------------------------------------------
    def calc_search_range(self, rating: float, game_type: str, time_in_queue: float) -> tuple[float, float]:
        """Return (min_rating, max_rating) a player can match against.

        Widens with time in queue and shrinks as more recent matches stack up.
        """
        percentile = BASE_PERCENTILE_RANGE / (len(self.recent_matches[game_type]) + 1)
        percentile += (percentile * time_in_queue / SEARCH_WIDEN_INTERVAL)

        rating_list = [ladders.ladders[game_type][user]["rating"] for user in ladders.ladders[game_type]]
        rating_list.append(rating)
        rating_list.append(0)
        rating_list.append(3000)
        pct_list = sorted(rating_list, reverse=True)

        rank = pct_list.index(rating)
        max_index = round(rank - (len(pct_list) * percentile))
        min_index = round(rank + (len(pct_list) * percentile))
        max_index = max(max_index, 0)
        min_index = min(min_index, len(pct_list) - 1)

        return pct_list[min_index], pct_list[max_index]

    # --- Player entry / exit ------------------------------------------------
    async def add_player(self, interaction, bot: commands.Bot, game_type: str) -> bool:
        """Add (or refresh) a player in a mode's queue. Returns False if the
        player still needs to register."""
        player_id = str(interaction.user.id)
        rio_name = rio_name_map.get_rio_name(player_id)
        if rio_name is None:
            embed = discord.Embed(
                title="Registration required",
                description="You must link your Project Rio username before joining the queue.\n"
                            f"Use `!register <rio_username>` in <#{BOT_SPAM_CHANNEL_ID}> to register.",
                color=0xFF5733)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return False

        rio_name_lower = rio_name.lower()
        player_rating = DEFAULT_RATING
        for user in ladders.ladders[game_type]:
            if user.lower() == rio_name_lower:
                player_rating = ladders.ladders[game_type][user]["rating"]
                break

        announcement: MatchAnnouncement | None = None
        async with self._lock:
            self.queues[game_type][player_id] = QueuedPlayer(
                discord_id=player_id,
                name=interaction.user.name,
                rating=player_rating,
                joined_at=time.time(),
            )
            min_rating, max_rating = self.calc_search_range(player_rating, game_type, 0)
            opponent_id = self._find_match(game_type, player_id, min_rating, max_rating)
            if opponent_id is not None:
                announcement = self._commit_match(game_type, player_id, opponent_id)

        if announcement is not None:
            await self._send_match(bot, announcement)
        await self.update_queue_status()
        return True

    async def remove_player(self, interaction):
        async with self._lock:
            self._remove_from_all(str(interaction.user.id))
        await self.update_queue_status()

    # --- Periodic refresh ---------------------------------------------------
    async def run_refresh(self, bot: commands.Bot):
        now = time.time()
        cutoff = now - RECENT_MATCH_WINDOW

        announcements: list[MatchAnnouncement] = []
        pings: list[tuple[str, str, str]] = []  # (role_id, role_name, game_type)
        afk_dm_ids: list[str] = []

        async with self._lock:
            # Prune the recent-match window; note if anything changed so the
            # status footer ("matches in the past hour") can refresh.
            recent_changed = False
            for m in ladders.GAME_MODES:
                before = len(self.recent_matches[m])
                self.recent_matches[m] = [t for t in self.recent_matches[m] if t > cutoff]
                if len(self.recent_matches[m]) != before:
                    recent_changed = True

            # Try to make one match per mode per tick (same as before).
            match_found = False
            for m in ladders.GAME_MODES:
                for pid in list(self.queues[m].keys()):
                    player = self.queues[m].get(pid)
                    if player is None:
                        continue  # already pulled into a match this tick
                    time_in_queue = now - player.joined_at
                    min_rating, max_rating = self.calc_search_range(player.rating, m, time_in_queue)
                    opponent_id = self._find_match(m, pid, min_rating, max_rating)
                    if opponent_id is not None:
                        announcements.append(self._commit_match(m, pid, opponent_id))
                        match_found = True
                        break

            # Gather notifications for everyone still waiting.
            for m in ladders.GAME_MODES:
                role_id, role_name = self._role_for_mode(m)
                for player in self.queues[m].values():
                    elapsed = now - player.joined_at
                    if elapsed >= PING_AFTER and now - self.last_ping_time[role_id] > PING_COOLDOWN:
                        self.last_ping_time[role_id] = now
                        pings.append((role_id, role_name, m))
                    if elapsed >= AFK_AFTER and not player.afk_reminded:
                        player.afk_reminded = True
                        afk_dm_ids.append(player.discord_id)

            update_needed = match_found or recent_changed

        # All Discord I/O happens after the lock is released.
        for announcement in announcements:
            await self._send_match(bot, announcement)

        channel = bot.get_channel(MATCH_CHANNEL_ID)
        for role_id, role_name, game_type in pings:
            embed = discord.Embed()
            embed.add_field(name=f'ATTENTION {role_name} GAMERS',
                            value="There is a player looking for a " + game_type + " match in queue!")
            await channel.send(role_id, embed=embed)

        for user_id in afk_dm_ids:
            try:
                user = await bot.fetch_user(user_id)
                embed = discord.Embed()
                embed.add_field(name="AFK Reminder",
                                value="You have been in the queue for 30 minutes. "
                                      "Please leave the queue if you have found a match or are no longer looking.")
                await user.send(embed=embed)
            except discord.Forbidden:
                logger.info("AFK DM forbidden for user %s", user_id)

        if update_needed or announcements:
            await self.update_queue_status()

    # --- Discord presentation ----------------------------------------------
    async def update_queue_status(self):
        if self.mm_message is None:
            return
        embed = build_status_embed(self.queues, self.recent_matches)
        try:
            await self.mm_message.edit(embed=embed)
        except discord.HTTPException:
            logger.exception("Failed to update queue status message")

    async def _send_match(self, bot: commands.Bot, ann: MatchAnnouncement):
        searcher = ann.searcher
        opponent = ann.opponent
        logger.info("%s %s match: %s %s vs %s %s", ann.number, ann.game_type,
                    searcher.name, searcher.rating, opponent.name, opponent.rating)

        channel = bot.get_channel(MATCH_CHANNEL_ID)
        mentions, embed, file = build_match_message(ann)
        await channel.send(mentions, embed=embed, file=file)
