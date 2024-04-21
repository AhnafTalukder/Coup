import asyncio
import random
import discord
import json
from discord.ext import commands

cardList = ['Assassin', 'Assassin', 'Assassin', 'Contessa', 'Contessa', 'Contessa',  'Duke', 'Duke', 'Duke',  'Captain', 'Captain','Captain', 'Ambassador', 'Ambassador', 'Ambassador', 'Spy', 'Spy'
            ,'Spy', 'Politician', 'Politician', 'Politician']

class Gameplay(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot
        self.name = ""
        self.coins = 2
        self.cards = []
        self.isAlive = True
        self.game_in_progress = False
        self.game_start_task = None


    @commands.command()
    async def start_game(self, ctx):
        with open('./data/gameplay.json', 'r') as f:
            gameplay_stat = json.load(f)

            if(gameplay_stat["game_in_progress"] == True):
                await ctx.send("A game is already in session.")
            else:
                gameplay_stat["game_in_progress"] = True

                await ctx.send("A game has been started. Once everyone has joined using !join_game, use !begin_game to start the game.")
                
                gameplay_stat["people_can_join"] = True
                gameplay_stat["game_ended"] = False

                with open('./data/gameplay.json', 'w') as file:
                    json.dump(gameplay_stat, file)

    @commands.command()
    async def begin_game(self, ctx):
         with open('./data/gameplay.json', 'r+') as f:
            gameplay_stat = json.load(f)

            if(gameplay_stat["game_in_progress"] == True):
                gameplay_stat["people_can_join"] = False
                await ctx.send("A game of Coup has begun.")

                with open('./data/gameplay.json', 'w') as file:
                    json.dump(gameplay_stat, file)
            else:
                await ctx.send("Please start a game using !start_game first.")

    @commands.command()
    async def join_game(self, ctx):

        with open('./data/gameplay.json', 'r') as f:
            gameplay_stat = json.load(f)

            if(gameplay_stat['people_can_join'] == False):
                await ctx.send("The time frame to join has been closed.")
                return

        self.name = ctx.author.display_name 
        self.cards = random.sample(cardList, 2)

        for card in self.cards:
            cardList.remove(card)

        with open('./data/players.json', 'r+') as f:
            players = json.load(f)

            for player in players:
                if player['username'] == self.name:
                    await ctx.send(f"{self.name} has already been added to the game.")
                    return
            
            new_player = [
                {"username": self.name, "coins": self.coins, "cards": self.cards, "isAlive": True}
            ]
            
            players.extend(new_player)

            f.seek(0)
            
            json.dump(players, f, indent = 4)
            
            f.truncate()

        await ctx.author.send(self.cards)
        await ctx.send(f"{self.name} has joined the Coup game.")

    @commands.command()
    async def check_coins(self, ctx, target: discord.Member = None):
        if target is None:
            target = ctx.author

        with open('./data/players.json', 'r+') as f:
            players = json.load(f)

        for player in players:

            if player['username'] == target.display_name:

                await ctx.send(f"{target.display_name} has {player['coins']} coin(s).")

                return

        await ctx.send(f"{target.display_name} has not joined the game.")

    @commands.command()
    async def check_cards(self, ctx, target: discord.Member = None):
        if target is None:
            target = ctx.author
        
        target_player_name = target.display_name

        with open('./data/players.json', 'r+') as f:
            players = json.load(f)
            target_player = next((player for player in players if player['username'] ==  target_player_name), None)

            if not target_player or not target_player['isAlive']:
                await ctx.send(f"Cannot find player {target_player_name} or the player is already out of the game.")
                return
            
            if target == ctx.author:
                card_message = "\n".join([f"({i + 1}) {card}" for i, card in enumerate(target_player['cards'])])
                await ctx.author.send(f"Here are your cards:\n{card_message}")
            else:
                num_cards = len(target_player['cards'])
                await ctx.send(f"{target_player_name} has {num_cards} card(s).")
    
    @commands.command()
    async def rules(self, ctx):
        help_message = (
            "**Welcome to Coup!**\n\n"
            "**Game Rules:**\n"
            "Coup is a game of deception and strategy. Each player starts with two cards, and the goal is to be the last player with influence left in the game.\n\n"
            "**Basic Commands:**\n"
            "- `!start_game`: Start the game.\n"
            "- `!begin_game`: Begin the game to start using abilities.\n"
            "- `!join_game`: Join the game.\n"
            "- `!check_coins [optional: @player]`: Check your coins or another player's coins.\n"
            "- `!check_cards [optional: @player]`: Check your cards or another player's cards.\n\n"
            "**Character Abilities:**\n"
            "- `!income`: Collect 1 coin.\n"
            "- `!foreign_aid`: Attempt to take 2 coins. Other players can block this action.\n"
            "- `!steal @player`: Attempt to steal 2 coins from another player. The target can block this action.\n"
            "- `!tax`: Collect 3 coins.\n"
            "- `!asassinate @player`:  Pay 3 coins to assasinate on of your opponent's cards. Blocked by Contessa.\n"
            "- `!coup @player`: Perform a coup against another player, forcing them to lose a card. Costs 7 coins.\n"
            "- `!exchange`: Take 2 cards, return 2 cards to Court deck. Cannot be blocked.\n"
            "- `!exile @player`: Force another player to reveal a card. Depending on your choice, they may exchange or keep the card, and you'll pay coins accordingly.\n\n"
            "**Challenge System:**\n"
            "Players can challenge certain actions made by other players if they suspect they are bluffing. React to the action message with 🚫 to block or 🤚 to challenge."
        )

        await ctx.send(help_message)


async def setup(bot):
    await bot.add_cog(Gameplay(bot))
