import asyncio
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from resources import EnvironmentVariables as ev

logger = logging.getLogger(__name__)

# Channel where players submit game results.
RANKED_BOT_CHANNEL_ID = ev.RANKED_BOT_CHANNEL_ID
# Only this Discord user may approve/deny manual submissions.
APPROVER_ID = ev.MANUAL_SUBMIT_APPROVER_ID

MANUAL_SUBMIT_ENDPOINT = "https://api.projectrio.app/manual_submit_game"
CHECK_EMOJI = "\U00002705"
X_EMOJI = "\U0000274C"
SUBMISSION_TIMEOUT = 86400.0  # 24 hours to approve/deny

# RIO key for manual submissions, loaded once at import rather than per command.
load_dotenv()
RIO_KEY = os.getenv("RIO_KEY")


class SubmitResults(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(help="type !submit <winner username> <winner score> <loser score> <loser username> <\"Game Mode Name\" (in quotes)>)")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def submit(self, ctx: commands.Context, user1: str, score1: int, score2: int,
                     user2: str, game_mode_name: str):
        if ctx.channel.id != RANKED_BOT_CHANNEL_ID:
            return

        await ctx.message.add_reaction(CHECK_EMOJI)
        await ctx.message.add_reaction(X_EMOJI)

        # DM the approver a link to the submission.
        try:
            approver = await ctx.bot.fetch_user(APPROVER_ID)
            dm_embed = discord.Embed()
            dm_embed.add_field(
                name="New Manual Submission",
                value=("A new manual submission has been created in the mario baseball server.\n"
                       f"`!submit {user1} {score1} {score2} {user2} \"{game_mode_name}\"`\n"
                       f"Please accept or deny it here: {ctx.message.jump_url}"))
            await approver.send(embed=dm_embed)
        except discord.Forbidden:
            logger.warning("Could not DM the manual-submission approver (%s)", APPROVER_ID)

        def check_confirm(rxn, usr):
            return (usr.id == APPROVER_ID
                    and rxn.emoji in (CHECK_EMOJI, X_EMOJI)
                    and rxn.message.id == ctx.message.id)

        try:
            reaction, _ = await self.client.wait_for('reaction_add', timeout=SUBMISSION_TIMEOUT,
                                                     check=check_confirm)
        except asyncio.TimeoutError:
            await ctx.send("Game was not accepted within 24 hours")
            return

        if reaction.emoji == X_EMOJI:
            await ctx.send(embed=self._result_embed(
                "Manual Submission Rejected", 0xFF5733, user1, score1, score2, user2, game_mode_name))
            return

        manual_submit = {
            "winner_username": user1,
            "loser_username": user2,
            "winner_score": score1,
            "loser_score": score2,
            "submitter_rio_key": RIO_KEY,
            "tag_set": game_mode_name,
            "date": round(ctx.message.created_at.timestamp()),
            "recalc": True,
        }
        async with self.client.session.post(MANUAL_SUBMIT_ENDPOINT, json=manual_submit) as response:
            if response.status >= 400:
                body = await response.text()
                logger.error("Manual submit failed (status %s): %s", response.status, body)
                fail_embed = discord.Embed(title="Manual Submission Failed", color=0xFF5733)
                fail_embed.add_field(
                    name="Error",
                    value=f"The Project Rio API rejected the submission (status {response.status}).")
                await ctx.send(embed=fail_embed)
                return

        await ctx.send(embed=self._result_embed(
            "Manual Submission Approved", 0x138F13, user1, score1, score2, user2, game_mode_name))

    @staticmethod
    def _result_embed(title: str, color: int, winner: str, winner_score: int,
                      loser_score: int, loser: str, game_mode: str) -> discord.Embed:
        embed = discord.Embed(title=title, color=color)
        embed.add_field(name="Winner", value=winner, inline=True)
        embed.add_field(name="Score", value=f"{winner_score} - {loser_score}", inline=True)
        embed.add_field(name="Loser", value=loser, inline=True)
        embed.add_field(name="Game Mode", value=game_mode, inline=False)
        return embed


async def setup(client):
    await client.add_cog(SubmitResults(client))
