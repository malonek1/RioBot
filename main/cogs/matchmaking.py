import logging

import discord
from discord import ButtonStyle
from discord.ext import commands, tasks
from matchmaker import BUTTON_CHANNEL_ID, Matchmaker
from resources import ladders

logger = logging.getLogger(__name__)

FEEDBACK_URL = "https://forms.gle/KNKwp86VFxrgkZiW9"


class QueueButton(discord.ui.Button):
    """Joins (or refreshes) a player in a single mode's queue."""

    def __init__(self, cog: "Matchmaking", mode: str):
        super().__init__(label=mode, style=ButtonStyle.blurple, custom_id=f"mm_queue:{mode}")
        self.cog = cog
        self.mode = mode

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if await self.cog.matchmaker.add_player(interaction, self.cog.bot, self.mode):
            self.cog.start_refresh_if_needed()
            embed = discord.Embed()
            embed.add_field(name='Queue Status:', value="You have entered the " + self.mode + " queue.")
            await interaction.followup.send(embed=embed, ephemeral=True)


class LeaveQueueButton(discord.ui.Button):
    """Removes a player from every mode's queue."""

    def __init__(self, cog: "Matchmaking"):
        super().__init__(label="Leave Queue", style=ButtonStyle.red, custom_id="mm_leave")
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.cog.matchmaker.remove_player(interaction)
        embed = discord.Embed()
        embed.add_field(name='Queue Status:', value="You have left the matchmaking queue.")
        await interaction.followup.send(embed=embed, ephemeral=True)


class MatchmakingView(discord.ui.View):
    """Persistent (timeout=None) view holding the queue buttons."""

    def __init__(self, cog: "Matchmaking"):
        super().__init__(timeout=None)
        for mode in ladders.GAME_MODES:
            self.add_item(QueueButton(cog, mode))
        self.add_item(LeaveQueueButton(cog))
        self.add_item(discord.ui.Button(label="Give Feedback", style=ButtonStyle.url, url=FEEDBACK_URL))


class Matchmaking(commands.Cog):
    """Owns the matchmaking Discord lifecycle: buttons and the refresh loop.

    The matching engine itself lives in matchmaking.Matchmaker; this cog just
    wires it to Discord.

    The refresh loop is *idle-aware*: it isn't started at load. A join starts it
    (start_refresh_if_needed); it stops itself once the queue drains. That stop
    is decided synchronously at the end of each tick, so a join that lands
    mid-tick is seen by has_waiting_players() and the loop won't wrongly stop.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.matchmaker = Matchmaker()
        # The button message is recreated once per process, not per reconnect.
        self._message_posted = False

    def cog_unload(self):
        if self.refresh_queue.is_running():
            self.refresh_queue.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        # on_ready fires on every (re)connect; only post the button message the
        # first time. The persistent view keeps working across reconnects for
        # the life of the process.
        if not self._message_posted:
            await self._post_queue_message()
            self._message_posted = True

    async def _post_queue_message(self):
        channel = self.bot.get_channel(BUTTON_CHANNEL_ID)
        if channel is None:
            logger.error("Button channel %s not found; cannot post queue message", BUTTON_CHANNEL_ID)
            return
        async for msg in channel.history():
            if msg.author == self.bot.user:
                await msg.delete()

        embed = discord.Embed()
        embed.add_field(name="Matchmaking queue initialized! Press buttons below to search for a game.",
                        value="Queue details will appear here when a user has entered the queue")
        view = MatchmakingView(self)
        self.matchmaker.mm_message = await channel.send(embed=embed, view=view)

    def start_refresh_if_needed(self):
        """Start the refresh loop if players are waiting and it isn't running."""
        if self.matchmaker.has_waiting_players() and not self.refresh_queue.is_running():
            self.refresh_queue.start()

    @tasks.loop(seconds=15)
    async def refresh_queue(self):
        try:
            await self.matchmaker.run_refresh(self.bot)
        except Exception:
            logger.exception("refresh_queue tick failed")
        # Idle-aware: stop once the queue has drained; a future join restarts us.
        if not self.matchmaker.has_waiting_players():
            self.refresh_queue.stop()

    @refresh_queue.before_loop
    async def before_refresh_queue(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(Matchmaking(bot))
