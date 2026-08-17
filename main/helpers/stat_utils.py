import discord

from resources import characters

BASE_STATS_URL = "https://api.projectrio.app/stats/"
FRONTEND_URL = "https://projectrio.pages.dev"


async def send_error_embed(ctx, message: str):
    embed = discord.Embed(title=message, color=0xEA7D07)
    await ctx.send(embed=embed)


async def send_stat_embed(ctx, title: str, desc: str, char: str):
    embed = discord.Embed(title=title, description=desc)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    embed.set_thumbnail(url=characters.images[char])
    await ctx.send(embed=embed)
