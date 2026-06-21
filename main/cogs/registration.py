from json import JSONDecodeError

import discord
from discord.ext import commands
from resources import rio_name_map, EnvironmentVariables as ev

MOD_ROLE_ID = ev.MOD_ROLE_ID
BOT_SPAM_CHANNEL_ID = ev.BOT_SPAM_CHANNEL_ID


class Registration(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(help="Link your Discord account to your Project Rio username. Example: !register pokebunny")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def register(self, ctx, rio_username: str):
        if ctx.channel.id != BOT_SPAM_CHANNEL_ID:
            embed = discord.Embed(color=0xEA7D07)
            embed.add_field(name="Wrong channel", value=f"Please use this command in <#{BOT_SPAM_CHANNEL_ID}>.")
            await ctx.send(embed=embed)
            return

        existing_owner = rio_name_map.find_discord_id_by_rio_name(rio_username)
        if existing_owner and existing_owner != str(ctx.author.id):
            embed = discord.Embed(
                title="Registration failed",
                description=f"**{rio_username}** is already linked to another Discord account. "
                            "If you believe this is an error, please contact a moderator.",
                color=0xFF5733)
            await ctx.send(embed=embed)
            return

        async with self.client.session.get(
            f"https://api.projectrio.app/games/?username={rio_username}&limit_games=1"
        ) as response:
            try:
                data = await response.json(content_type=None)
            except JSONDecodeError:
                data = {}

        if response.status != 200 or "error" in data or not data:
            embed = discord.Embed(
                title="Registration failed",
                description=f"No Project Rio account found with username **{rio_username}**. "
                            "Please check the spelling and try again.",
                color=0xFF5733)
            await ctx.send(embed=embed)
            return

        rio_name_map.set_rio_name(str(ctx.author.id), rio_username)
        embed = discord.Embed(color=0x00CC44)
        embed.add_field(
            name="Registration successful!",
            value=f"Your Discord account is now linked to Rio username **{rio_username}**.")
        await ctx.send(embed=embed)

    @commands.command(help="Remove your Project Rio username registration")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def unregister(self, ctx):
        if ctx.channel.id != BOT_SPAM_CHANNEL_ID:
            embed = discord.Embed(color=0xEA7D07)
            embed.add_field(name="Wrong channel", value=f"Please use this command in <#{BOT_SPAM_CHANNEL_ID}>.")
            await ctx.send(embed=embed)
            return

        if rio_name_map.remove_rio_name(str(ctx.author.id)):
            embed = discord.Embed(color=0xEA7D07)
            embed.add_field(name="Unregistered", value="Your Rio username link has been removed.")
        else:
            embed = discord.Embed(color=0xEA7D07)
            embed.add_field(name="Not registered", value="You don't have a Rio username linked. Use `!register <rio_username>` to link your account.")
        await ctx.send(embed=embed)

    @commands.command(help="Check what Rio username is linked to a Discord account. Example: !whois @user")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def whois(self, ctx, user: discord.Member = None):
        target = user or ctx.author
        rio_name = rio_name_map.get_rio_name(str(target.id))
        embed = discord.Embed(color=0xEA7D07)
        if rio_name:
            embed.add_field(name=f"{target.display_name}'s Rio Username", value=f"**{rio_name}**")
        else:
            embed.add_field(
                name=f"{target.display_name}",
                value="No Rio username linked. Use `!register <rio_username>` to link your account."
            )
        await ctx.send(embed=embed)

    @commands.command(help="[Mod] Link a Discord user to a Rio username. Example: !link @user pokebunny")
    @commands.has_role(MOD_ROLE_ID)
    async def link(self, ctx, user: discord.Member, rio_username: str):
        notes = []
        prev_rio_name = rio_name_map.get_rio_name(str(user.id))
        if prev_rio_name and prev_rio_name.lower() != rio_username.lower():
            notes.append(f"Replaced {user.display_name}'s previous link (**{prev_rio_name}**).")
        prev_owner_id = rio_name_map.find_discord_id_by_rio_name(rio_username)
        if prev_owner_id and prev_owner_id != str(user.id):
            prev_owner = ctx.guild.get_member(int(prev_owner_id))
            prev_name = prev_owner.display_name if prev_owner else f"<@{prev_owner_id}>"
            notes.append(f"Removed **{rio_username}** from {prev_name}'s registration.")

        rio_name_map.set_rio_name(str(user.id), rio_username)
        value = f"{user.display_name} is now linked to Rio username **{rio_username}**."
        if notes:
            value += "\n" + "\n".join(notes)
        embed = discord.Embed(color=0x00CC44)
        embed.add_field(name="Link successful!", value=value)
        await ctx.send(embed=embed)

    @commands.command(help="[Mod] Remove the Rio username link for a Discord user. Example: !unlink @user")
    @commands.has_role(MOD_ROLE_ID)
    async def unlink(self, ctx, user: discord.Member):
        if rio_name_map.remove_rio_name(str(user.id)):
            embed = discord.Embed(color=0xEA7D07)
            embed.add_field(name="Unlinked", value=f"{user.display_name}'s Rio username link has been removed.")
        else:
            embed = discord.Embed(color=0xEA7D07)
            embed.add_field(name="Not linked", value=f"{user.display_name} doesn't have a Rio username linked.")
        await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(Registration(client))
