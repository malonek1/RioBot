import discord
from discord.ext import commands


class Memes(commands.Cog):
    def __init__(self, client):
        self.client = client

    # guy.jpg
    @commands.command()
    async def guy(self, ctx):
        await ctx.send('<:Guy:927712162829451274>')

    # peacock
    @commands.command()
    async def peacock(self, ctx):
        await ctx.send(':peacock:')

    # goombo
    @commands.command()
    async def dingus(self, ctx):
        await ctx.send('<:goombo:987231921916510228>')

    # washed copypasta
    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def washed(self, ctx):
        embed = discord.Embed()
        embed.add_field(name="WASHED",
                        value="I would've won if i hadn't taken a break for a long time, scored more runs than you, "
                              "played only top tier competition, didn't waste my time, gave up less runs than you, "
                              "and I can beat remkey again anyway, and i did it for the people, and i only play top "
                              "players so i don't know this matchup")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def rayveean(self, ctx):
        embed = discord.Embed()
        embed.add_field(name='RAYVEEAN HURT MY FEELINGS:',
                        value="Rayveean changed my name to dignus and it really hurts my feelings inside. But I won't admit that to him because that would be embarassing")
        await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(Memes(client))
