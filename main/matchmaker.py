import asyncio
import bisect
import logging
import time

import discord
from discord.ext import commands
from models.matchmaking import MatchAnnouncement, QueuedPlayer
from resources import EnvironmentVariables as ev
from resources import ladders, rio_name_map
from services.matchmaking_embeds import build_match_message, build_status_embed

logger = logging.getLogger(__name__)

# --- Tunable constants -------------------------------------------------------
# Starting percentile range for matchmaking search.
BASE_PERCENTILE_RANGE = 0.5
# Divisor controlling how quickly the search range widens with time in queue.
SEARCH_WIDEN_INTERVAL = 120
# Default rating assigned to players who aren't on the ladder yet.
DEFAULT_RATING = 1300
# Outer bounds used when a player's search band runs past the ends of the
# ladder population ("match anyone lower / higher").
RATING_FLOOR = 0.0
RATING_CEILING = 3000.0
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
        self.recent_matches: dict[str, list[float]] = {m: [] for m in ladders.GAME_MODES}
        self.last_ping_time: dict[str, float] = {STARS_OFF_ROLE: 0.0, STARS_ON_ROLE: 0.0}
        self.mm_message: discord.Message | None = None

    def has_waiting_players(self) -> bool:
        """True if anyone is queued in any mode. Drives the idle-aware loop."""
        return any(self.queues[m] for m in ladders.GAME_MODES)

    def _recent_match_count(self, game_type: str, now: float) -> int:
        """Matches in this mode within the recent window.

        Computed live (not via len) so the search-range calc and status footer
        stay correct even when the idle-aware loop hasn't pruned in a while.
        """
        cutoff = now - RECENT_MATCH_WINDOW
        return sum(1 for t in self.recent_matches[game_type] if t > cutoff)

    # --- Queue mutation (lock-protected) ------------------------------------
    def _remove_from_all(self, player_id: str):
        for m in ladders.GAME_MODES:
            self.queues[m].pop(player_id, None)

    def _find_matches(self, game_type: str, now: float) -> list[MatchAnnouncement]:
        """Pair up everyone matchable in a mode and commit those matches.

        A match is a property of a *pair*, not a player: a pair is eligible if
        EITHER player's (time-widened) range covers the other's rating. Eligible
        pairs are taken closest-rating-first, each player used at most once, so
        multiple matches can form in one pass and the result doesn't depend on
        queue insertion order.
        """
        mode_queue = self.queues[game_type]
        if len(mode_queue) < 2:
            return []

        # Widened range per player, computed once up front so commits during the
        # greedy pass don't shift anyone's range mid-pass.
        recent_count = self._recent_match_count(game_type, now)
        ranges = {
            pid: self.calc_search_range(p.rating, game_type, now - p.joined_at, recent_count)
            for pid, p in mode_queue.items()
        }

        pids = list(mode_queue.keys())
        eligible: list[tuple[float, str, str]] = []  # (rating gap, a, b)
        for i in range(len(pids)):
            for j in range(i + 1, len(pids)):
                a, b = pids[i], pids[j]
                rating_a, rating_b = mode_queue[a].rating, mode_queue[b].rating
                a_min, a_max = ranges[a]
                b_min, b_max = ranges[b]
                if (a_min <= rating_b <= a_max) or (b_min <= rating_a <= b_max):
                    eligible.append((abs(rating_a - rating_b), a, b))

        eligible.sort(key=lambda pair: pair[0])
        used: set[str] = set()
        announcements: list[MatchAnnouncement] = []
        for _gap, a, b in eligible:
            if a in used or b in used:
                continue
            used.add(a)
            used.add(b)
            announcements.append(self._commit_match(game_type, a, b))
        return announcements

    def _commit_match(self, game_type: str, id_a: str, id_b: str) -> MatchAnnouncement:
        """Remove both players from every queue and record the match. Lock held."""
        player_a = self.queues[game_type][id_a]
        player_b = self.queues[game_type][id_b]
        self._remove_from_all(id_a)
        self._remove_from_all(id_b)
        self.recent_matches[game_type].append(time.time())
        return MatchAnnouncement(game_type=game_type, player_a=player_a, player_b=player_b)

    @staticmethod
    def _role_for_mode(game_type: str) -> tuple[str, str]:
        if game_type in (ladders.STARS_ON_MODE, ladders.BIG_BALLA):
            return STARS_ON_ROLE, "STARS-ON"
        # Stars-off, hazards, randoms and anything else default to stars-off.
        return STARS_OFF_ROLE, "STARS-OFF"

    # --- Search range -------------------------------------------------------
    @staticmethod
    def calc_search_range(
        rating: float, game_type: str, time_in_queue: float, recent_count: int
    ) -> tuple[float, float]:
        """Return (min_rating, max_rating) a player can match against.

        The band is a percentile window of the ladder population centred on the
        player's rank: it widens with time waited and narrows as recent matches
        pile up (an active queue means good pairings are likely, so stay picky).
        Past the population's edges the band opens up to RATING_FLOOR/CEILING,
        i.e. "match anyone lower / higher".
        """
        percentile = BASE_PERCENTILE_RANGE / (recent_count + 1)
        percentile += percentile * time_in_queue / SEARCH_WIDEN_INTERVAL

        ranked = ladders.get_sorted_ratings(game_type)  # ascending
        population = len(ranked)
        if population == 0:
            return RATING_FLOOR, RATING_CEILING

        band = round(population * percentile)
        # Player's rank from the top = how many ladder players outrank them.
        above = population - bisect.bisect_right(ranked, rating)

        def edge_rating(rank_from_top: int) -> float:
            if rank_from_top < 0:
                return RATING_CEILING
            if rank_from_top > population - 1:
                return RATING_FLOOR
            return ranked[population - 1 - rank_from_top]

        max_rating = edge_rating(above - band)
        min_rating = edge_rating(above + band)
        return min_rating, max_rating

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
                color=0xFF5733,
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return False

        player_rating = ladders.get_player_rating(game_type, rio_name, DEFAULT_RATING)

        now = time.time()
        async with self._lock:
            self.queues[game_type][player_id] = QueuedPlayer(
                discord_id=player_id,
                name=interaction.user.name,
                rating=player_rating,
                joined_at=now,
            )
            announcements = self._find_matches(game_type, now)

        for announcement in announcements:
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

            # Pair up everyone matchable, across every mode.
            for m in ladders.GAME_MODES:
                announcements.extend(self._find_matches(m, now))

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

            update_needed = bool(announcements) or recent_changed

        # All Discord I/O happens after the lock is released.
        for announcement in announcements:
            await self._send_match(bot, announcement)

        if pings:
            channel = bot.get_channel(MATCH_CHANNEL_ID)
            if channel is None:
                logger.error("Match channel %s not found; cannot send queue pings", MATCH_CHANNEL_ID)
            else:
                for role_id, role_name, game_type in pings:
                    embed = discord.Embed()
                    embed.add_field(
                        name=f"ATTENTION {role_name} GAMERS",
                        value=f"There is a player looking for a {game_type} match in queue!",
                    )
                    await channel.send(role_id, embed=embed)

        for user_id in afk_dm_ids:
            try:
                user = await bot.fetch_user(user_id)
                embed = discord.Embed()
                embed.add_field(
                    name="AFK Reminder",
                    value="You have been in the queue for 30 minutes. "
                    "Please leave the queue if you have found a match or are no longer looking.",
                )
                await user.send(embed=embed)
            except discord.Forbidden:
                logger.info("AFK DM forbidden for user %s", user_id)

        if update_needed:
            await self.update_queue_status()

    # --- Discord presentation ----------------------------------------------
    async def update_queue_status(self):
        if self.mm_message is None:
            return
        now = time.time()
        recent_counts = {m: self._recent_match_count(m, now) for m in ladders.GAME_MODES}
        embed = build_status_embed(self.queues, recent_counts)
        try:
            await self.mm_message.edit(embed=embed)
        except discord.HTTPException:
            logger.exception("Failed to update queue status message")

    async def _send_match(self, bot: commands.Bot, ann: MatchAnnouncement):
        a, b = ann.player_a, ann.player_b
        logger.info("%s match: %s %s vs %s %s", ann.game_type, a.name, a.rating, b.name, b.rating)

        channel = bot.get_channel(MATCH_CHANNEL_ID)
        if channel is None:
            logger.error("Match channel %s not found; cannot announce match", MATCH_CHANNEL_ID)
            return
        mentions, embed, file = build_match_message(ann)
        await channel.send(mentions, embed=embed, file=file)
