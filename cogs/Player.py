import discord
import json
import random
import asyncio
from discord.ext import commands
from discord import File

cardList = ['Assasin', 'Assasin', 'Assasin', 'Contessa', 'Contessa', 'Contessa',  'Duke', 'Duke', 'Duke',  'Captain', 'Captain','Captain', 'Ambassador', 'Ambassador', 'Ambassador', 'Spy', 'Spy'
            ,'Spy', 'Politician', 'Politician', 'Politician']

class Player(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.name = ""
        self.coins = 2
        self.cards = []
        self.isAlive = True

     

    @commands.command()
    async def income(self, ctx):
        with open('./data/players.json', 'r+') as f:

            players = json.load(f)

            # Find the player issuing the command
            pl = next((p for p in players if p['username'] == ctx.author.display_name), None)

            # Check if the player exists and their isAlive status
            if pl is None:
                await ctx.send("You are not registered in the game.")
                return

            if not pl['isAlive']:
                await ctx.send("You cannot use this command because you are not alive in the game.")
                return
            
            found = False
            for player in players:
                if player['username'] == ctx.author.display_name:
                     found = True
                     if(player['isAlive'] == False):
                        await send('Dead player cannot collect income.')
                        return
                     player['coins'] += 1
                     self.coins = player['coins']

            if(found == False):
                await ctx.send(f'{ctx.author.display_name} has not joined the game.')
            
            f.seek(0)
            
            json.dump(players, f, indent=4)
            
            f.truncate()

        await ctx.send(f"{ctx.author.display_name} collected income. Total coins: {self.coins}")

    @commands.command()
    async def foreign_aid(self, ctx):
        with open('./data/players.json', 'r+') as a:
                play = json.load(a)
                pl = next((p for p in play if p['username'] == ctx.author.display_name), None)

                # Check if the player exists and their isAlive status
                if pl is None:
                    await ctx.send("You are not registered in the game.")
                    return

                if not pl['isAlive']:
                    await ctx.send("You cannot use this command because you are not alive in the game.")
                    return
        
        msg = await ctx.send(f"{ctx.author.display_name} is trying to take foreign aid. React with 🚫 to block.")
        await msg.add_reaction('🚫')

        def check(reaction, user):
            return user != ctx.author and user != self.bot.user and str(reaction.emoji) == '🚫' and reaction.message.id == msg.id

        try:
            reaction, blocker = await self.bot.wait_for('reaction_add', timeout=5.0, check=check)
            await self.handle_foreign_aid_block(ctx, blocker, ctx.author)  # Pass the ctx.author as the challenged user
        except asyncio.TimeoutError:
            await ctx.send(f"No one blocked {ctx.author.display_name}'s foreign aid.")
            # Foreign aid was not blocked, add coins
            with open('./data/players.json', 'r+') as f:
                players = json.load(f)
                for player in players:
                    if player['username'] == ctx.author.display_name:
                        player['coins'] += 2  # Each foreign aid grants 2 coins
                
                f.seek(0)
                json.dump(players, f, indent=4)
                f.truncate()

    async def handle_foreign_aid_block(self, ctx, blocker, challenged):
        # Message to react for both blocking the block using 'Spy' and challenging the original block
        follow_up_msg = await ctx.send(
            f"{blocker.display_name} has blocked the foreign aid with 'Duke'. "
            "React with 🚫 to block the block using 'Spy', or react with 🤚 to challenge the initial block."
        )
        await follow_up_msg.add_reaction('🚫')
        await follow_up_msg.add_reaction('🤚')

        def follow_up_check(reaction, user):
            return (
                user == ctx.author and
                str(reaction.emoji) in ['🚫', '🤚'] and
                reaction.message.id == follow_up_msg.id
            )

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=5.0, check=follow_up_check)
            if str(reaction.emoji) == '🚫':
                # React with 🤚 to challenge this new block
                follow_up_msg2 = await ctx.send(
                    f"{ctx.author.display_name} is attempting to block {blocker.display_name}'s Duke block using 'Spy'. "
                    "React with 🤚 to challenge this new block."
                )
                await follow_up_msg2.add_reaction('🤚')

                def challenge_new_block_check(reaction, user):
                    return user != self.bot.user and str(reaction.emoji) == '🤚' and reaction.message.id == follow_up_msg2.id

                try:
                    reaction, challenger = await self.bot.wait_for('reaction_add', timeout=5.0, check=challenge_new_block_check)
                    await self.challenge(ctx, 'block_duke_by_spy', challenger, blocker)  # Use 'challenger' and 'blocker' correctly
                except asyncio.TimeoutError:
                    await ctx.send("No challenge made within 5 seconds, the 'Spy' block stands.")
            elif str(reaction.emoji) == '🤚':
                # Handle challenge directly
                await self.challenge(ctx, 'block_foreign_aid', ctx.author, blocker)  # ctx.author challenges the blocker
        except asyncio.TimeoutError:
            await ctx.send("No action taken within 5 seconds, foreign aid is blocked.")

    @commands.command()
    async def coup(self, ctx, target: discord.Member):
        if ctx.author == target:
            await ctx.send("You cannot perform a coup on yourself.")
            return

        target_player_name = target.display_name

        with open('./data/players.json', 'r+') as f:
            players = json.load(f)
            current_player = next((p for p in players if p['username'] == ctx.author.display_name), None)

            if current_player is None:
                await ctx.send("You are not registered in the game.")
                return

            if not current_player['isAlive']:
                await ctx.send("You cannot use this command because you are not alive in the game.")
                return

            if current_player['coins'] < 7:
                await ctx.send("You need at least 7 coins to perform a coup.")
                return

            current_player['coins'] -= 7

            target_player = next((player for player in players if player['username'] == target_player_name), None)

            if not target_player or not target_player['isAlive']:
                await ctx.send(f"Cannot find player {target_player_name} or the player is already out of the game.")
                return

            card_message = "\n".join([f"({i+1}) {card}" for i, card in enumerate(target_player['cards'])])
            message = await ctx.send(f"{target_player_name} has been couped! Please choose a card to lose by reacting with the corresponding emoji:\n{card_message}")
            await message.add_reaction("1️⃣")
            await message.add_reaction("2️⃣")

            def check(reaction, user):
                return user == target and str(reaction.emoji) in ["1️⃣", "2️⃣"]

            reaction, user = await self.bot.wait_for('reaction_add', check=check)
            card_to_lose = 1 if str(reaction.emoji) == "1️⃣" else 2

            target_player['cards'].pop(card_to_lose - 1)

            # Check if the target player has any cards left
            if not target_player['cards']:
                target_player['isAlive'] = False
                await ctx.send(f"{target_player_name} has no more cards and is now out of the game.")
            else:
                await ctx.send(f"{target_player_name} has lost one of their player cards.")

            # Update the player data
            f.seek(0)
            json.dump(players, f, indent=4)
            f.truncate()

    @commands.command()
    async def challenge(self, ctx, action: str, challenger_user: discord.Member, challenged_user: discord.Member):
        with open('./data/players.json', 'r+') as f:
            players = json.load(f)

            # Assigning challenger and challenged based on parameters
            challenger = next((player for player in players if player['username'] == challenger_user.display_name), None)
            challenged = next((player for player in players if player['username'] == challenged_user.display_name), None)

            if not challenger or not challenged:
                await ctx.send("One or both users are not in the game.")
                return

            # Mapping actions to the required cards
            action_to_card = {
                'steal': ('steal from', 'Captain'),
                'block_foreign_aid': ('block foreign aid', 'Duke'),
                'block_duke_by_spy': ('counter-block a Duke\'s block', 'Spy'),
                'exile': ('exile', 'Politician'),
                'block_exile_by_spy': ('block exile as Spy', 'Spy'),
                'block_steal_by_ambassador': ('block a steal as Ambassador', 'Ambassador'),
                'block_steal_by_captain': ('block a steal as Captain', 'Captain'),
                'tax': ('collect tax', 'Duke')
            }

            if action not in action_to_card:
                await ctx.send("Invalid action to challenge.")
                return

            action_name, action_card = action_to_card[action]

            # Handling the challenge outcome
            if action_card in challenged['cards']:
                # Challenged successfully shows card
                await ctx.send(f"{challenged_user.display_name} successfully shows a {action_card}.")
                challenged['cards'].remove(action_card)
                cardList.append(action_card)  # Assuming cardList is managed globally
                new_card = random.choice(cardList)
                challenged['cards'].append(new_card)
                cardList.remove(new_card)

                # Challenger loses a card if the challenge fails
                await self.handle_card_loss(challenger_user, challenger['cards'], ctx)
            else:
                # Challenged loses a card if they fail to show the required card
                await self.handle_card_loss(challenged_user, challenged['cards'], ctx)

            f.seek(0)
            json.dump(players, f, indent=4)
            f.truncate()

    async def handle_card_loss(self, user, cards, ctx):
        """Handle the loss of a card and update if player is out of the game."""
        emojis = ["1️⃣", "2️⃣"]
        msg = await ctx.send(f"{user.display_name} has lost the challenge. React to lose one of your cards.")
        for emoji in emojis[:len(cards)]:
            await msg.add_reaction(emoji)

        def check(reaction, user_check):
            return user_check == user and str(reaction.emoji) in emojis[:len(cards)]

        reaction, user_reacted = await self.bot.wait_for('reaction_add', check=check)
        card_to_lose = cards.pop(emojis.index(str(reaction.emoji)))
        cardList.append(card_to_lose)

        if not cards:
            # Player has lost all cards and is now considered dead
            await ctx.send(f"{user.display_name} has no more cards and is out of the game.")
            # Update player's status in the database or json file
            player = next((p for p in self.players if p['username'] == user.display_name), None)
            if player:
                player['isAlive'] = False
        else:
            await ctx.send(f"{user.display_name} has lost a card.")




    @commands.command()
    async def steal(self, ctx, target: discord.Member):
        with open('./data/players.json', 'r+') as a:
            play = json.load(a)
            pl = next((p for p in play if p['username'] == ctx.author.display_name), None)

            # Check if the player exists and their isAlive status
            if pl is None:
                await ctx.send("You are not registered in the game.")
                return

            if not pl['isAlive']:
                await ctx.send("You cannot use this command because you are not alive in the game.")
                return
        
        if ctx.author == target:
            await ctx.send("You can't steal from yourself.")
            return

        msg = await ctx.send(
            f"{ctx.author.display_name} is trying to steal from {target.display_name}."
            "\nReact with 🚓 to block with Captain."
            "\nReact with 🎩 to block with Ambassador."
            "\nReact with 🤚 to challenge."
        )
        reactions = {'🚓': 'block_steal_by_captain', '🎩': 'block_steal_by_ambassador', '🤚': 'steal'}
        for emoji in reactions:
            await msg.add_reaction(emoji)

        def check(reaction, user):
            return user != ctx.author and user != self.bot.user and str(reaction.emoji) in reactions and reaction.message.id == msg.id

        try:
            reaction, reactor = await self.bot.wait_for('reaction_add', timeout=5.0, check=check)
            action = reactions[str(reaction.emoji)]
            if action == 'steal':
                await self.challenge(ctx, action, reactor, ctx.author)
            else:
                follow_up_msg = await ctx.send(
                    f"{reactor.display_name} is blocking the steal attempt with a {action.split('_')[-1].capitalize()}."
                    " React with 🤚 to challenge this block."
                )
                await follow_up_msg.add_reaction('🤚')

                def challenge_check(reaction, challenger):
                    return challenger == ctx.author and str(reaction.emoji) == '🤚' and reaction.message.id == follow_up_msg.id

                try:
                    reaction, _ = await self.bot.wait_for('reaction_add', timeout=5.0, check=challenge_check)
                    if reaction.emoji == '🤚':
                        await self.challenge(ctx, action, ctx.author, reactor)
                except asyncio.TimeoutError:
                    await ctx.send(f"No one challenged the block. {reactor.display_name}'s block stands.")
                    return
        except asyncio.TimeoutError:
            # No reaction to block or challenge within the timeout, proceed with the steal
            with open('./data/players.json', 'r+') as f:
                players = json.load(f)
                target_player = next((player for player in players if player['username'] == target.display_name), None)
                stealing_player = next((player for player in players if player['username'] == ctx.author.display_name), None)
                if target_player['coins'] > 0:
                    stolen_amount = 1 if target_player['coins'] == 1 else 2
                    target_player['coins'] -= stolen_amount
                    stealing_player['coins'] += stolen_amount
                    await ctx.send(f"{ctx.author.display_name} successfully stole {stolen_amount} coins from {target.display_name}.")
                else:
                    await ctx.send(f"{target.display_name} has no coins to steal.")

                f.seek(0)
                json.dump(players, f, indent=4)
                f.truncate()

    @commands.command()
    async def tax(self, ctx):
        with open('./data/players.json', 'r+') as a:
            play = json.load(a)
            pl = next((p for p in play if p['username'] == ctx.author.display_name), None)

            # Check if the player exists and their isAlive status
            if pl is None:
                await ctx.send("You are not registered in the game.")
                return

            if not pl['isAlive']:
                await ctx.send("You cannot use this command because you are not alive in the game.")
                return
            
        file_path = r".\images\Duke.png"
        file = File(file_path, filename="Duke.png")
        await ctx.send(f"{ctx.author.display_name} is claiming to be a Duke and attempting to collect tax. React with '🤚' to challenge.", file=file)
        msg = await ctx.send("React with '🤚' within 5 seconds to challenge.")
        await msg.add_reaction('🤚')

        def check_challenge(reaction, user):
            return user != self.bot.user and user != ctx.author and str(reaction.emoji) == '🤚'

        try:
            # Wait for a challenge reaction
            reaction, challenger = await self.bot.wait_for('reaction_add', timeout=5.0, check=check_challenge)
            # If a challenge is made, handle the challenge using the updated challenge function signature
            if reaction and challenger:
                await self.challenge(ctx, 'tax', challenger, ctx.author)  # pass both the challenger and the challenged (ctx.author)
                await ctx.send(f"Challenge has been processed.")
            else:
                await ctx.send("No valid challenge was made.")
        except asyncio.TimeoutError:
            # No challenge within the timeout
            await ctx.send("No challenge was made within the time limit.")

        # Collect tax if no challenge or challenge was unsuccessful
        with open('./data/players.json', 'r+') as f:
            players = json.load(f)
            for player in players:
                if player['username'] == ctx.author.display_name:
                    player['coins'] += 3  # Add coins
                    await ctx.send(f"{ctx.author.display_name} successfully collected tax. Total coins now: {player['coins']}.")
                    break
            f.seek(0)
            json.dump(players, f, indent=4)
            f.truncate()

    @commands.command()
    async def exchange(self, ctx):
        with open('./data/players.json', 'r+') as f:
            players = json.load(f)

            for player in players:
                if player['username'] == ctx.author.display_name:

                    # Pull two random cards, remove them from the deck, and add them to hand
                    firstcard = random.sample(cardList, 1)
                    secondcard = random.sample(cardList, 1)

                    # Remove the cards from the deck
                    for card in cardList:
                        if card == firstcard or card == secondcard:
                            cardlist.remove(card)
                    
                    # Add the cards to hand
                    player['cards'].append(firstcard)
                    player['cards'].append(secondcard)

                    self.cards = player['cards']

                    await ctx.author.send(self.cards)

                    # Prompt the user to react
                    msg = await ctx.author.send(f'Choose which of your cards to return to the deck')

                    await msg.add_reaction('1️⃣')
                    await msg.add_reaction('2️⃣')
                    await msg.add_reaction('3️⃣')
                    
                    if len(player['cards']) == 4:
                        await msg.add_reaction('4️⃣')
                    
                    # Check the user's reaction and place the desired cards back in the deck
                    def check(reaction, user):
                            return user == ctx.author and str(reaction.emoji) in ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout = 60.0, check = check)
                    except asyncio.TimeoutError:
                        await ctx.send(f'No response from {ctx.author.display_name}')
                    else: 
                        if str(reaction.emoji) == '1️⃣':
                            cardList.append(player['cards'].pop(0))

                        elif str(reaction.emoji) == '2️⃣':
                            cardList.append(player['cards'].pop(1))
                        elif str(reaction.emoji) == '3️⃣':
                            cardList.append(player['cards'].pop(2))
                        elif str(reaction.emoji) == '4️⃣':
                            cardList.append(player['cards'].pop(3))

                    # Do it again
                    msg = await ctx.author.send(f'Choose another card to return to the deck')

                    await msg.add_reaction('1️⃣')
                    await msg.add_reaction('2️⃣')
                      
                    if len(player['cards']) == 3:
                        await msg.add_reaction('3️⃣')
                    
                    # Check the user's reaction and place the desired cards back in the deck
                    def check(reaction, user):
                            return user == ctx.author and str(reaction.emoji) in ['1️⃣', '2️⃣', '3️⃣']
                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout = 20, check = check)
                    except asyncio.TimeoutError:
                        await ctx.send(f'No response from {ctx.author.display_name}')
                    else: 
                        if str(reaction.emoji) == '1️⃣':
                            cardList.append(player['cards'].pop(0))
                        elif str(reaction.emoji) == '2️⃣':
                            cardList.append(player['cards'].pop(1))
                        elif str(reaction.emoji) == '3️⃣':
                            cardList.append(player['cards'].pop(2))
                

            # Go to the beginning of the file
            f.seek(0)
        
            # Write updated data to file
            json.dump(players, f, indent=4)
            
            # Truncate any remaining data
            f.truncate()

        await ctx.send(f"{ctx.author.display_name} exchanged influence cards.")

    @commands.command()
    async def exile(self, ctx, target: discord.Member):
        with open('./data/players.json', 'r+') as a:
            play = json.load(a)
            pl = next((p for p in play if p['username'] == ctx.author.display_name), None)

            # Check if the player exists and their isAlive status
            if pl is None:
                await ctx.send("You are not registered in the game.")
                return

            if not pl['isAlive']:
                await ctx.send("You cannot use this command because you are not alive in the game.")
                return
            
        target_player_name = target.display_name

        with open('./data/players.json', 'r+') as f:
            players = json.load(f)
            target_player = next((player for player in players if player['username'] == target_player_name), None)

        if not target_player or not target_player['isAlive']:
            await ctx.send(f"Cannot find player {target_player_name} or the player is already out of the game.")
            return

        # Announce the exile attempt and provide options for blocking or challenging
        msg = await ctx.send(
            f"{ctx.author.display_name} is attempting to exile {target_player_name}. React with 🚫 to block or 🤚 to challenge."
        )
        await msg.add_reaction("🚫")  # No entry emoji for block
        await msg.add_reaction("🤚")  # Hand emoji for challenge

        def check(reaction, user):
            return user != ctx.author and user != self.bot.user and str(reaction.emoji) in ["🚫", "🤚"] and reaction.message.id == msg.id

        try:
            reaction, reactor = await self.bot.wait_for('reaction_add', timeout=5.0, check=check)
            if str(reaction.emoji) == "🚫":
                # Handle the block
                follow_up_msg = await ctx.send(
                    f"{reactor.display_name} has blocked the exile using 'Spy'. {ctx.author.display_name}, react with 🤚 to challenge this block."
                )
                await follow_up_msg.add_reaction("🤚")  # Ensure the hand emoji for challenging the block is added
                try:
                    reaction, challenger = await self.bot.wait_for('reaction_add', timeout=5.0, check=lambda r, u: u == ctx.author and str(r.emoji) == '🤚' and r.message.id == follow_up_msg.id)
                    if reaction:
                        await self.challenge(ctx, 'block_exile_by_spy', ctx.author, reactor)  # Challenger is ctx.author, challenged is the reactor
                except asyncio.TimeoutError:
                    await ctx.send("No challenge was made to the block. The exile is blocked.")
            elif str(reaction.emoji) == "🤚":
                # Handle the challenge
                await self.challenge(ctx, 'exile', reactor, ctx.author)  # Challenger is reactor, challenged is ctx.author
        except asyncio.TimeoutError:
            await ctx.send("No reactions. Proceeding with exile.")

            card_message = "\n".join([f"({i+1}) {card}" for i, card in enumerate(target_player['cards'])])
            message = await target.send(f"{target_player_name}, please choose a card to reveal by reacting with the corresponding emoji:\n{card_message}")
            await message.add_reaction("1️⃣")
            await message.add_reaction("2️⃣")

            def check(reaction, user):
                return user == target and str(reaction.emoji) in ["1️⃣", "2️⃣"]

            reaction, user = await self.bot.wait_for('reaction_add', check=check)
            card_to_reveal = 1 if str(reaction.emoji) == "1️⃣" else 2

            revealed_card = target_player['cards'].pop(card_to_reveal - 1)

            await ctx.author.send(f"{target_player_name} has revealed the card: {revealed_card}")

            message = await ctx.author.send("Do you want to force the player to exchange the card (react with 🔄) for 1 coin, or force them to keep the card (react with 🚫) for 2 coins?")
            await message.add_reaction("🔄")  
            await message.add_reaction("🚫") 

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["🔄", "🚫"]

            reaction, user = await self.bot.wait_for('reaction_add', check=check)

            if str(reaction.emoji) == "🔄":
                if target_player['coins'] < 1:
                    await ctx.author.send("You don't have enough coins to force the player to exchange the card.")
                    return
                target_player['coins'] -= 1
                new_card = random.choice(cardList)
                target_player['cards'].append(new_card)
                cardList.remove(new_card)
                cardList.append(revealed_card)
                await ctx.author.send(f"You have forced {target_player_name} to exchange the card.")
                await target.send(f"{ctx.author.display_name} has forced you to exchange your card. You now have the card: {new_card}")
            else:
                if target_player['coins'] < 2:
                    await ctx.author.send("You don't have enough coins to force the player to keep the card.")
                    return
                target_player['coins'] -= 2
                target_player['cards'].append(revealed_card)
                await ctx.author.send(f"You have forced {target_player_name} to keep the card: {revealed_card}")
                await target.send(f"{ctx.author.display_name} has forced you to keep your card: {revealed_card}")

        with open('./data/players.json', 'w') as f:
            json.dump(players, f, indent=4)
            f.truncate()



async def setup(bot):
    await bot.add_cog(Player(bot))