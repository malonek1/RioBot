import logging

import discord
from discord import ButtonStyle
from discord.ext import commands, tasks

from resources import ladders
from matchmaking import Matchmaker, BUTTON_CHANNEL_ID

logger = logging.getLogger(__name__)

FEEDBACK_URL = "https://forms.gle/KNKwp86VFxrgkZiW9"


class QueueButton(discord.ui.Button):
    """Joins (or refreshes) a player in a single mode's queue."""

    def __init__(self, matchmaker: Matchmaker, bot: commands.Bot, mode: str):
        super().__init__(label=mode, style=ButtonStyle.blurple, custom_id=f"mm_queue:{mode}")
        self.matchmaker = matchmaker
        self.bot = bot
        self.mode = mode

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if await self.matchmaker.add_player(interaction, self.bot, self.mode):
            embed = discord.Embed()
            embed.add_field(name='Queue Status:', value="You have entered the " + self.mode + " queue.")
            await interaction.followup.send(embed=embed, ephemeral=True)


class LeaveQueueButton(discord.ui.Button):
    """Removes a player from every mode's queue."""

    def __init__(self, matchmaker: Matchmaker):
        super().__init__(label="Leave Queue", style=ButtonStyle.red, custom_id="mm_leave")
        self.matchmaker = matchmaker

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.matchmaker.remove_player(interaction)
        embed = discord.Embed()
        embed.add_field(name='Queue Status:', value="You have left the matchmaking queue.")
        await interaction.followup.send(embed=embed, ephemeral=True)


class MatchmakingView(discord.ui.View):
    """Persistent (timeout=None) view holding the queue buttons."""

    def __init__(self, matchmaker: Matchmaker, bot: commands.Bot):
        super().__init__(timeout=None)
        for mode in ladders.GAME_MODES:
            self.add_item(QueueButton(matchmaker, bot, mode))
        self.add_item(LeaveQueueButton(matchmaker))
        self.add_item(discord.ui.Button(label="Give Feedback", style=ButtonStyle.url, url=FEEDBACK_URL))


class Matchmaking(commands.Cog):
    """Owns the matchmaking Discord lifecycle: buttons and the refresh loop.

    The matching engine itself lives in matchmaking.Matchmaker; this cog just
    wires it to Discord.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.matchmaker = Matchmaker()
        # The button message is recreated once per process, not per reconnect.
        self._message_posted = False

    async def cog_load(self):
        # Safe to start here: the loop's before_loop waits for the gateway to be
        # ready before the first tick (we can't wait_until_ready in cog_load
        # itself — that runs inside setup_hook, before the bot connects).
        self.refresh_queue.start()

    def cog_unload(self):
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
        async for msg in channel.history():
            if msg.author == self.bot.user:
                await msg.delete()

        embed = discord.Embed()
        embed.add_field(name="Matchmaking queue initialized! Press buttons below to search for a game.",
                        value="Queue details will appear here when a user has entered the queue")
        view = MatchmakingView(self.matchmaker, self.bot)
        self.matchmaker.mm_message = await channel.send(embed=embed, view=view)

    @tasks.loop(seconds=15)
    async def refresh_queue(self):
        try:
            await self.matchmaker.run_refresh(self.bot)
        except Exception:
            logger.exception("refresh_queue tick failed")

    @refresh_queue.before_loop
    async def before_refresh_queue(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(Matchmaking(bot))
