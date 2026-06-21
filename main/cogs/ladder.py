from discord.ext import commands
import discord
import urllib.parse
from resources import EnvironmentVariables as ev, ladders
from helpers.stat_utils import FRONTEND_URL

ROWS_PER_PAGE = 25


def _build_pages(header, rows):
    if not rows:
        return [header + "\nNo results."]
    pages = []
    for i in range(0, len(rows), ROWS_PER_PAGE):
        pages.append(header + "\n" + "\n".join(rows[i:i + ROWS_PER_PAGE]))
    return pages


def _make_embed(title, url, pages, page):
    embed = discord.Embed(title=title, color=0xEA7D07)
    if url:
        embed.url = url
    embed.description = f"```{pages[page]}```"
    if len(pages) > 1:
        embed.set_footer(text=f"Page {page + 1} of {len(pages)}")
    return embed


class LadderView(discord.ui.View):
    def __init__(self, title, url, pages, plain=False):
        super().__init__(timeout=86400)
        self.title = title
        self.url = url
        self.pages = pages
        self.page = 0
        self.plain = plain
        self.message = None
        self._sync_buttons()

    def _sync_buttons(self):
        self.prev_button.disabled = self.page == 0
        self.next_button.disabled = self.page == len(self.pages) - 1

    def current_embed(self):
        return _make_embed(self.title, self.url, self.pages, self.page)

    def current_content(self):
        lines = [f"**{self.title}**", f"```{self.pages[self.page]}```"]
        if len(self.pages) > 1:
            lines.append(f"Page {self.page + 1} of {len(self.pages)}")
        return "\n".join(lines)

    async def _edit(self, interaction):
        if self.plain:
            await interaction.response.edit_message(content=self.current_content(), view=self)
        else:
            await interaction.response.edit_message(embed=self.current_embed(), view=self)

    async def on_timeout(self):
        if self.message:
            await self.message.edit(view=None)

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page -= 1
        self._sync_buttons()
        await self._edit(interaction)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        self._sync_buttons()
        await self._edit(interaction)


class Ladder(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def _wrong_channel(self, ctx):
        embed = discord.Embed(color=0xEA7D07)
        embed.add_field(name='The !ladder command must be used here:', value=f'<#{ev.BOT_SPAM_CHANNEL_ID}>')
        await ctx.send(embed=embed)

    async def _fetch_ladder(self, mode):
        await ladders.refresh_ladders()
        mode = ladders.find_game_mode(mode)
        ladder_values = sorted(ladders.ladders[mode].values(), key=lambda x: x["adjusted_rating"], reverse=True)
        return mode, ladder_values

    @commands.command(help="display the ladder")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def ladder(self, ctx, mode="off"):
        if ctx.channel.id != ev.BOT_SPAM_CHANNEL_ID:
            await self._wrong_channel(ctx)
            return

        mode, ladder_values = await self._fetch_ladder(mode)

        header = f"{'#':<5}{'Username':<18}{'Rtg':<7}{'W/L':<9}Pct"
        rows = []
        for index, user in enumerate(ladder_values):
            if user["num_wins"] == 0 and user["num_losses"] == 0:
                continue
            total = user["num_wins"] + user["num_losses"]
            win_pct = user["num_wins"] / total * 100
            wl = f"{user['num_wins']}-{user['num_losses']}"
            username_display = user["username"][:17] + "…" if len(user["username"]) > 18 else user["username"]
            rows.append(
                f"{str(index + 1) + '.':<5}{username_display:<18}{round(user['adjusted_rating']):<7}{wl:<9}{round(win_pct, 1)}%"
            )

        url = f"{FRONTEND_URL}/modes/{urllib.parse.quote(mode)}/ladder"
        pages = _build_pages(header, rows)
        view = LadderView(f"{mode} Ladder", url, pages)
        view.message = await ctx.send(embed=view.current_embed(), view=view if len(pages) > 1 else None)

    @commands.command(name="ladderCompact", help="Display the ladder in a compact view. Parameters: [mode] [min_games]")
    @commands.cooldown(1, 2, commands.BucketType.default)
    async def ladder_compact(self, ctx, mode="off", min_games=5):
        if ctx.channel.id != ev.BOT_SPAM_CHANNEL_ID:
            await self._wrong_channel(ctx)
            return

        mode, ladder_values = await self._fetch_ladder(mode)
        filtered = [u for u in ladder_values if u["num_wins"] + u["num_losses"] >= min_games]

        longest_elo = max((len(str(round(u["adjusted_rating"]))) for u in filtered), default=3)
        elo_col = longest_elo + 2

        header = f"{'#':<5}{'Username':<16}{'Rtg':<{elo_col}}W/L"
        rows = []
        for pos, user in enumerate(filtered, 1):
            username_display = user["username"][:13] + "…" if len(user["username"]) > 14 else user["username"]
            wl = f"{user['num_wins']}-{user['num_losses']}"
            rows.append(f"{str(pos) + '.':<5}{username_display:<16}{str(round(user['adjusted_rating'])):<{elo_col}}{wl}")

        pages = _build_pages(header, rows)
        view = LadderView(f"{mode} Compact Ladder (Min {min_games} games)", None, pages, plain=True)
        view.message = await ctx.send(content=view.current_content(), view=view if len(pages) > 1 else None)


async def setup(client):
    await client.add_cog(Ladder(client))
