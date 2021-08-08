import discord
import os


client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$quote'):
        await message.channel.send('This is a cry for help!')

client.run(os.getenv('TOKEN'))