import discord
import os
import random

quotes = []

def addQuote(quote):
    quotes.append(quote)

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$cry'):
        await message.channel.send('This is a cry for help!')

    if message.content.startswith('$add'):
        await message.channel.send('Enter your quote here:')

        def check(msg):
            return msg.author == message.author and msg.channel == message.channel

        msg = await client.wait_for("message", check=check)
        addQuote(msg.content)
        await message.channel.send('Quote added!')

    if message.content.startswith('$quote'):
        await message.channel.send('"' + random.choice(quotes) + '"')

client.run(os.getenv('TOKEN'))