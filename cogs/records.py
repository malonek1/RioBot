from re import search

import discord
from discord.ext import commands
from resources import SheetsParser
class Records(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def record(self, ctx, player_1: discord.Member):
        print("Entering record function")
        player_0 = ctx.author
        print(f'{player_0.id}' + " " + f'{player_1.id}')
        game_array = SheetsParser.get_record(f'{player_0.id}', f'{player_1.id}')
        print("Re-entering record function")

        new_game_array_1 = game_array[0]
        new_game_array_2 = game_array[1]
        #print(new_game_array_1)
        #print(new_game_array_2)

        #match = [rc for rc in new_game_array_1 if 'R2' in new_game_array_1[0]]
        #print(match)

        #Need a loop that can find matching row values between both users within the nested array
        match_1 = []
        #print(len(new_game_array_1))
        #print(str(new_game_array_1[0])[6:10])
        for item in new_game_array_1:
            match_1.append(str(item))

        #print(str(new_game_array_2[0])[6:10])
        match_2 = []
        for item in new_game_array_2:
            match_2.append(str(item))

        print(match_1)
        print(match_2)

        sub_wins = 0
        opp_wins = 0

        count = 0
        for sub in match_1:
            count = count + 1
            for opp in match_2:
                if count < 9:
                    if sub[6:8] in opp[6:8]:
                        if "C1" in sub:
                            sub_wins = sub_wins + 1
                        elif "C1" in opp:
                            opp_wins = opp_wins + 1
                elif 99 > count >= 9:
                    if sub[6:9] in opp[6:9]:
                        if "C1" in sub:
                            sub_wins = sub_wins + 1
                        elif "C1" in opp:
                            opp_wins = opp_wins + 1
                elif 999 > count >= 99:
                    if sub[6:10] in opp[6:10]:
                        if "C1" in sub:
                            sub_wins = sub_wins + 1
                        elif "C1" in opp:
                            opp_wins = opp_wins + 1

        print("\n")
        print(sub_wins)
        print(opp_wins)

        print("\n")
        print(game_array[0])
        print(game_array[1])
        print("\n")
        print(str(game_array[1][1])[6:8])
        print(type(game_array[1][1]))

        embed = discord.Embed()
        embed.add_field(name=f'{player_0.name} game record against {player_1.name}:',
                        value=f'{sub_wins} Wins \n{opp_wins} Losses')
        await ctx.send(embed=embed)

async def setup(client):
    await client.add_cog(Records(client))