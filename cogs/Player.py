import discord
import json
import random
import asyncio
from discord.ext import commands
from discord import File

cardList = ['Assassin', 'Assassin', 'Assassin', 'Contessa', 'Contessa', 'Contessa',  'Duke', 'Duke', 'Duke',  'Captain', 'Captain','Captain', 'Ambassador', 'Ambassador', 'Ambassador', 'Spy', 'Spy'
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
        file_path = r".\images\Income.png"
        file = File(file_path, filename="Income.png")
        with open('./data/players.json', 'r+') as f:

            players = json.load(f)

            pl = next((p for p in players if p['username'] == ctx.author.display_name), None)

            if pl is None:
                await ctx.send("You are not registered in the game.")
                return

            if not pl['isAlive']:
                await ctx.send("You cannot use this command because you are not alive in the game.")
                return
            
            # initial_coins = pl['coins']
            found = False
            for player in players:
                if player['username'] == ctx.author.display_name:
                     found = True
                     if(player['isAlive'] == False):
                        await ctx.send('Dead player cannot collect income.')
                        return
                     player['coins'] += 1
                     self.coins = player['coins']
                    #  pl['coins'] += 1
                    #  coins_test_passed = pl['coins'] == initial_coins + 1
                    # if coins_test_passed:
                    #     print("Coins Test Passed: Player's coin amount increased by one.")
                    # else:
                    #     print("Coins Test Failed: Player's coin amount did not increase as expected.")

            if(found == False):
                await ctx.send(f'{ctx.author.display_name} has not joined the game.')
            
            f.seek(0)
            
            json.dump(players, f, indent=4)
            
            f.truncate()

        await ctx.send(f"{ctx.author.display_name} collected income. Total coins: {self.coins}", file = file)

    @commands.command()
    async def foreign_aid(self, ctx):
        file_path = r".\images\Aid.png"
        file = File(file_path, filename="Aid.png")
        with open('./data/players.json', 'r+') as a:
                play = json.load(a)
                pl = next((p for p in play if p['username'] == ctx.author.display_name), None)
                # initial_coins = pl['coins']
                # pl['coins'] += 2 

                if pl is None:
                    await ctx.send("You are not registered in the game.")
                    return

                if not pl['isAlive']:
                    await ctx.send("You cannot use this command because you are not alive in the game.")
                    return
                
        # coins_test_passed = pl['coins'] == initial_coins + 2
        msg = await ctx.send(f"{ctx.author.display_name} is trying to take foreign aid. React with 🚫 to block.", file = file)
        await msg.add_reaction('🚫')

        def check(reaction, user):
            return user != ctx.author and user != self.bot.user and str(reaction.emoji) == '🚫' and reaction.message.id == msg.id

        try:
            reaction, blocker = await self.bot.wait_for('reaction_add', timeout=5.0, check=check)
            await self.handle_foreign_aid_block(ctx, blocker, ctx.author)  
        except asyncio.TimeoutError:
            await ctx.send(f"No one blocked {ctx.author.display_name}'s foreign aid.")
            with open('./data/players.json', 'r+') as f:
                players = json.load(f)
                for player in players:
                    if player['username'] == ctx.author.display_name:
                        player['coins'] += 2
                        self.coins = player['coins']  
                        await ctx.send(f"{ctx.author.display_name} collected foreign aid. Total coins: {self.coins}")
                        # if coins_test_passed:
                        #     print("Coins Test Passed: Player's coin amount increased by two.")
                        # else:
                        #     print("Coins Test Failed: Player's coin amount did not increase as expected.")
                
                f.seek(0)
                json.dump(players, f, indent=4)
                f.truncate()

    async def handle_foreign_aid_block(self, ctx, blocker, challenged):
        file_path2 = r".\images\Duke.png"
        file2 = File(file_path2, filename="Duke.png")
        follow_up_msg = await ctx.send(
            f"{blocker.display_name} has blocked the foreign aid with 'Duke'. "
            "React with 🚫 to block the block using 'Spy', or react with 🤚 to challenge the initial block.", file = file2
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
                file_path3 = r".\images\Aid.png"
                file3 = File(file_path3, filename="Aid.png")
                follow_up_msg2 = await ctx.send(
                    f"{ctx.author.display_name} is attempting to block {blocker.display_name}'s Duke block using 'Spy'. "
                    "React with 🤚 to challenge this new block.", file = file3
                )
                await follow_up_msg2.add_reaction('🤚')

                def challenge_new_block_check(reaction, user):
                    return user != self.bot.user and str(reaction.emoji) == '🤚' and reaction.message.id == follow_up_msg2.id

                try:
                    reaction, challenger = await self.bot.wait_for('reaction_add', timeout=5.0, check=challenge_new_block_check)
                    await self.challenge(ctx, 'block_duke_by_spy', blocker, ctx.author)  
                except asyncio.TimeoutError:
                    await ctx.send("No challenge made within 5 seconds, the 'Spy' block stands.")
            elif str(reaction.emoji) == '🤚':
                await self.challenge(ctx, 'block_foreign_aid', ctx.author , blocker) 
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

            # initial_coins = current_player['coins']
            # initial_card_count = len(target_player['cards'])

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
            message = await ctx.send(f"{target_player_name} has been couped! Please choose a card to lose by reacting with the corresponding emoji.")
            emojis = ["1️⃣", "2️⃣"]
            for emoji in emojis[:len(target_player['cards'])]:
                    await message.add_reaction(emoji)


            def check(reaction, user):
                return user == target and str(reaction.emoji) in ["1️⃣", "2️⃣"]

            reaction, user = await self.bot.wait_for('reaction_add', check=check)
            card_to_lose = 1 if str(reaction.emoji) == "1️⃣" else 2

            target_player['cards'].pop(card_to_lose - 1)

            # coins_test_passed = current_player['coins'] == initial_coins - 7
            # cards_test_passed = len(target_player['cards']) == initial_card_count - 1

            f.seek(0)
            json.dump(players, f, indent=4)
            f.truncate()

            # if coins_test_passed:
            #     print("Coins Test Passed: Coin amount decreased by seven.")
            # else:
            #     print("Coins Test Failed: Coin amount did not decrease as expected.")

            # if cards_test_passed:
            #     print("Cards Test Passed: Target player has lost a card.")
            # else:
            #     print("Cards Test Failed: Target player card count did not decrease as expected.")

            with open('./data/players.json', 'r+') as f:
                players = json.load(f)

                player = next((p for p in players if p['username'] == target.display_name), None)

                if player is None:
                    await ctx.send("Player not found.")
                    return

                if len(player['cards']) == 0:
                    player['isAlive'] = False
                    await ctx.send(f"{player['username']} has no more cards and is now out of the game.")

                    f.seek(0)  
                    json.dump(players, f, indent=4)
                    f.truncate()  
                else:
                    await ctx.send(f"{target_player_name} has lost a card.")
        await self.check_winner(ctx)
          
    async def check_winner(self, ctx):
        file_path = r".\images\Winner.png"
        file = File(file_path, filename="Winner.png")
        with open('./data/players.json', 'r') as f:
            players = json.load(f)
            alive_players = [player for player in players if player['isAlive']]

        if len(alive_players) == 1:
            await ctx.send(f"{alive_players[0]['username']} is the winner!", file = file)
            with open('./data/gameplay.json', 'r+') as g:
                gameplay = json.load(g)
                gameplay['game_in_progress'] = False
                gameplay['people_can_join'] = False
                gameplay['game_ended'] = True
                g.seek(0)
                json.dump(gameplay, g, indent=4)
                g.truncate()

            initial_data = [{
                "username": "",
                "coins": "",
                "cards": [],
                "isAlive": False
            }]

            with open('./data/players.json', 'w') as f:
                json.dump(initial_data, f, indent=4)  
            return True
        return False

    @commands.command()
    async def challenge(self, ctx, action: str, challenger_user: discord.Member, challenged_user: discord.Member):
        with open('./data/players.json', 'r+') as f:
            players = json.load(f)

            challenger = next((player for player in players if player['username'] == challenger_user.display_name), None)
            challenged = next((player for player in players if player['username'] == challenged_user.display_name), None)

            if not challenger or not challenged:
                await ctx.send("One or both users are not in the game.")
                return

            action_to_card = {
                'steal': ('steal from', 'Captain'),
                'block_foreign_aid': ('block foreign aid', 'Duke'),
                'block_duke_by_spy': ('counter-block a Duke\'s block', 'Spy'),
                'exile': ('exile', 'Politician'),
                'exchange': ('exchange', 'Ambassador'),
                'block_exile_by_spy': ('block exile as Spy', 'Spy'),
                'block_steal_by_ambassador': ('block a steal as Ambassador', 'Ambassador'),
                'block_steal_by_captain': ('block a steal as Captain', 'Captain'),
                'tax': ('collect tax', 'Duke')
            }

            if action not in action_to_card:
                await ctx.send("Invalid action to challenge.")
                return

            action_name, action_card = action_to_card[action]

            if action_card in challenged['cards']:
                # initial_card_count_challenged = len(challenged['cards'])

                await ctx.send(f"{challenged_user.display_name} successfully shows a {action_card}.")
                challenged['cards'].remove(action_card)
                cardList.append(action_card)  
                new_card = random.choice(cardList)
                challenged['cards'].append(new_card)
                cardList.remove(new_card)

                # truthful_test_passed = len(challenged['cards']) == initial_card_count_challenged 

                emojis = ["1️⃣", "2️⃣"]
                msg = await ctx.send(f"{challenger_user.display_name} has lost the challenge. React to lose one of your cards.")
                for emoji in emojis[:len(challenger['cards'])]:
                    await msg.add_reaction(emoji)

                def check(reaction, user):
                    return user == challenger_user and str(reaction.emoji) in emojis[:len(challenger['cards'])]

                reaction, user = await self.bot.wait_for('reaction_add', check=check)
                card_to_lose = challenger['cards'].pop(emojis.index(str(reaction.emoji)))
                cardList.append(card_to_lose)

                await ctx.send(f"{challenger_user.display_name} has lost a card.")

                if len(challenger['cards']) == 0:
                    challenger['isAlive'] = False
                    await ctx.send(f"{challenger_user.display_name} has no more cards and is now out of the game.")

                # if truthful_test_passed:
                #     print("Truthful Challenge Test Passed: Challenged player did not lose a card.")
                # else:
                #     print("Truthful Challenge Test Failed: The card count did not remain as expected for a truthful challenge.")
            else:
                # initial_card_count_challenged = len(challenged['cards'])

                emojis = ["1️⃣", "2️⃣"]
                msg = await ctx.send(f"{challenged_user.display_name} has lost the challenge. React to lose one of your cards.")
                for emoji in emojis[:len(challenged['cards'])]:
                    await msg.add_reaction(emoji)

                def check(reaction, user):
                    return user == challenged_user and str(reaction.emoji) in emojis[:len(challenged['cards'])]

                reaction, user = await self.bot.wait_for('reaction_add', check=check)
                card_to_lose = challenged['cards'].pop(emojis.index(str(reaction.emoji)))
                cardList.append(card_to_lose)

                # bluffing_test_passed = len(challenged['cards']) == initial_card_count_challenged - 1

                await ctx.send(f"{challenged_user.display_name} has lost a card.")

                if len(challenged['cards']) == 0:
                    challenged['isAlive'] = False
                    await ctx.send(f"{challenged_user.display_name} has no more cards and is now out of the game.")
    
            f.seek(0)
            json.dump(players, f, indent=4)
            f.truncate()

            # if bluffing_test_passed:
            #     print("Bluffing Challenge Test Passed: Challenged player lost a card.")
            # else:
            #     print("Bluffing Challenge Test Failed: The card count did not decrease as expected for a bluffing challenge.")

            await self.check_winner(ctx)

    @commands.command()
    async def steal(self, ctx, target: discord.Member):
        file_path = r".\images\Captain.png"
        file = File(file_path, filename="Captain.png")
        with open('./data/players.json', 'r+') as a:
            play = json.load(a)
            pl = next((p for p in play if p['username'] == ctx.author.display_name), None)

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
            "\nReact with 🤚 to challenge.", file = file
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
            with open('./data/players.json', 'r+') as f:
                players = json.load(f)
                target_player = next((player for player in players if player['username'] == target.display_name), None)
                stealing_player = next((player for player in players if player['username'] == ctx.author.display_name), None)

                # initial_coins_stealing_player = stealing_player['coins']
                # initial_coins_target_player = target_player['coins']

                if target_player['coins'] > 0:
                    stolen_amount = 1 if target_player['coins'] == 1 else 2
                    target_player['coins'] -= stolen_amount
                    stealing_player['coins'] += stolen_amount

                    # steal_test_passed = (
                    # stealing_player['coins'] == initial_coins_stealing_player + stolen_amount and
                    # target_player['coins'] == initial_coins_target_player - stolen_amount
                    # )

                    # if steal_test_passed:
                    #     print(f"Steal Test Passed: {ctx.author.display_name} successfully stole {stolen_amount} coins from {target.display_name}.")
                    # else:
                    #     print(f"Steal Test Failed: Coin transfer did not occur as expected during steal.")

                    await ctx.send(f"{ctx.author.display_name} successfully stole {stolen_amount} coins from {target.display_name}.")
                else:
                    await ctx.send(f"{target.display_name} has no coins to steal.")

                f.seek(0)
                json.dump(players, f, indent=4)
                f.truncate()

    @commands.command()
    async def tax(self, ctx):
        with open('./data/players.json', 'r+') as a:
            players = json.load(a)
            player = next((p for p in players if p['username'] == ctx.author.display_name), None)

            if player is None:
                await ctx.send("You are not registered in the game.")
                return

            if not player['isAlive']:
                await ctx.send("You cannot use this command because you are not alive in the game.")
                return

            # initial_coins = player['coins']

        file_path = r".\images\Duke.png"
        file = File(file_path, filename="Duke.png")
        await ctx.send(f"{ctx.author.display_name} is claiming to be a Duke and attempting to collect tax. React with '🤚' to challenge.", file=file)
        msg = await ctx.send("React with '🤚' within 5 seconds to challenge.")
        await msg.add_reaction('🤚')

        def check_challenge(reaction, user):
            return user != self.bot.user and user != ctx.author and str(reaction.emoji) == '🤚'

        try:
            reaction, challenger = await self.bot.wait_for('reaction_add', timeout=5.0, check=check_challenge)
            if reaction:
                await self.challenge(ctx, 'tax', challenger, ctx.author) 
                return  
        except asyncio.TimeoutError:
            await ctx.send("No challenge was made within the time limit.")

        with open('./data/players.json', 'r+') as f:
            players = json.load(f)
            player = next((p for p in players if p['username'] == ctx.author.display_name), None)
            if player:
                player['coins'] += 3

                # coins_test_passed = player['coins'] == initial_coins + 3
                # if coins_test_passed:
                #     print("Coins Test Passed: Coin amount increased by three.")
                # else:
                #     print("Coins Test Failed: Coin amount did not increase as expected.")

                await ctx.send(f"{ctx.author.display_name} successfully collected tax. Total coins now: {player['coins']}.")

            f.seek(0)
            json.dump(players, f, indent=4)
            f.truncate()

    @commands.command()
    async def exile(self, ctx, target: discord.Member):
        file_path = r".\images\Politician.png"
        file = File(file_path, filename="Politician.png")
        with open('./data/players.json', 'r+') as a:
            play = json.load(a)
            pl = next((p for p in play if p['username'] == ctx.author.display_name), None)

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
            current_player = next((player for player in players if player['username'] == ctx.author.display_name), None)

        if not target_player or not target_player['isAlive']:
            await ctx.send(f"Cannot find player {target_player_name} or the player is already out of the game.")
            return

        msg = await ctx.send(
            f"{ctx.author.display_name} is attempting to exile {target_player_name}. React with 🚫 to block or 🤚 to challenge.", file = file
        )
        await msg.add_reaction("🚫") 
        await msg.add_reaction("🤚")  

        def check(reaction, user):
            return user != ctx.author and user != self.bot.user and str(reaction.emoji) in ["🚫", "🤚"] and reaction.message.id == msg.id

        try:
            reaction, reactor = await self.bot.wait_for('reaction_add', timeout=5.0, check=check)
            if str(reaction.emoji) == "🚫":
                file_path2 = r".\images\Spy.png"
                file2 = File(file_path2, filename="Spy.png")
                follow_up_msg = await ctx.send(
                    f"{reactor.display_name} has blocked the exile using 'Spy'. {ctx.author.display_name}, react with 🤚 to challenge this block.", file = file2
                )
                await follow_up_msg.add_reaction("🤚")  
                try:
                    reaction, challenger = await self.bot.wait_for('reaction_add', timeout=5.0, check=lambda r, u: u == ctx.author and str(r.emoji) == '🤚' and r.message.id == follow_up_msg.id)
                    if reaction:
                        await self.challenge(ctx, 'block_exile_by_spy', ctx.author, reactor)  
                except asyncio.TimeoutError:
                    await ctx.send("No challenge was made to the block. The exile is blocked.")
            elif str(reaction.emoji) == "🤚":
                await self.challenge(ctx, 'exile', reactor, ctx.author)  
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
                if current_player['coins'] < 1:
                    await ctx.author.send("You don't have enough coins to force the player to exchange the card.")
                    return
                current_player['coins'] -= 1
                new_card = random.choice(cardList)
                target_player['cards'].append(new_card)
                cardList.remove(new_card)
                cardList.append(revealed_card)
                await ctx.author.send(f"You have forced {target_player_name} to exchange the card.")
                await target.send(f"{ctx.author.display_name} has forced you to exchange your card. You now have the card: {new_card}")
            else:
                if current_player['coins'] < 2:
                    await ctx.author.send("You don't have enough coins to force the player to keep the card.")
                    return
                current_player['coins'] -= 2
                target_player['cards'].append(revealed_card)
                await ctx.author.send(f"You have forced {target_player_name} to keep the card: {revealed_card}")
                await target.send(f"{ctx.author.display_name} has forced you to keep your card: {revealed_card}")

        with open('./data/players.json', 'w') as f:
            json.dump(players, f, indent=4)
            f.truncate()

    @commands.command()
    async def assassinate(self, ctx, target: discord.Member):
        if ctx.author == target:
            await ctx.send("You cannot assassinate yourself!")
            return

        with open('./data/players.json', 'r+') as f:
            players = json.load(f)
            assassin = next((player for player in players if player['username'] == ctx.author.display_name), None)
            victim = next((player for player in players if player['username'] == target.display_name), None)

            if not assassin or not victim:
                await ctx.send("One or both users have not joined the game.")
                return
            if not assassin['isAlive']:
                await ctx.send('Dead players cannot assassinate anyone.')
                return
            if assassin['coins'] < 3:
                await ctx.send("You do not have enough coins to assassinate someone!")
                return
            if not victim['isAlive']:
                await ctx.send(f'{target.display_name} is already dead and cannot be assassinated!')
                return

            # initial_coins_assassin = assassin['coins']
            # initial_card_count_victim = len(victim['cards'])

            assassin['coins'] -= 3
            await ctx.send(f"{ctx.author.display_name} now has {assassin['coins']} coins.")

            msg = await ctx.send(f"{ctx.author.display_name} is attempting to assassinate {target.display_name}. React with 🚫 to block or ✋ to challenge within 5 seconds.")
            await msg.add_reaction('🚫')
            await msg.add_reaction('✋')

            def check(reaction, user):
                return user != self.bot.user and user != ctx.author and str(reaction.emoji) in ['🚫', '✋']

            try:
                reaction, reactor = await self.bot.wait_for('reaction_add', timeout=5.0, check=check)
                if str(reaction.emoji) == '🚫':
                    msg_block = await ctx.send(f"{reactor.display_name} claims to block with Contessa. React with ✋ to challenge this block.")
                    await msg_block.add_reaction('✋')

                    try:
                        reaction_challenge, challenger = await self.bot.wait_for('reaction_add', timeout=5.0, check=lambda r, u: u != self.bot.user and u != reactor and str(r.emoji) == '✋')
                        if challenger:
                            reactor_player = next((player for player in players if player['username'] == reactor.display_name), None)
                            if 'Contessa' in [card for player in players if player['username'] == reactor.display_name for card in player['cards']]:
                                await ctx.send(f"{reactor.display_name} successfully shows a Contessa.")
                                challenger_player = next((player for player in players if player['username'] == challenger.display_name), None)
                                await self.card_loss(ctx, challenger_player)
                            else:
                                await ctx.send(f"{reactor.display_name} does not have a Contessa.")
                                await self.card_loss(ctx, reactor_player)
                    except asyncio.TimeoutError:
                        await ctx.send(f"No challenges were made. {reactor.display_name}'s block is successful.")
                elif str(reaction.emoji) == '✋':
                    if 'Assassin' in [card for player in players if player['username'] == ctx.author.display_name for card in player['cards']]:
                        await ctx.send(f"{ctx.author.display_name} confirms an Assassin card.")
                        await self.card_loss(ctx, victim)
                    else:
                        await ctx.send(f"{ctx.author.display_name} does not have an Assassin card.")
                        await self.card_loss(ctx, assassin)

            except asyncio.TimeoutError:
                await ctx.send(f"No one responded in time. {target.display_name} has been successfully assassinated!")
                await self.card_loss(ctx, victim)

            # coins_test_passed = assassin['coins'] == initial_coins_assassin - 3
            # cards_test_passed = (not any(reaction.emoji == '🚫' for reaction, user in reactions_received)
            #                     and len(victim['cards']) == initial_card_count_victim - 1)

            # if coins_test_passed:
            #     print("Coins Test Passed: Assassin's coin amount decreased by three.")
            # else:
            #     print("Coins Test Failed: Assassin's coin amount did not decrease as expected.")

            # if cards_test_passed:
            #     print("Cards Test Passed: Victim has lost a card.")
            # else:
            #     print("Cards Test Failed: Victim's card count did not decrease as expected.")

            f.seek(0)
            json.dump(players, f, indent=4)
            f.truncate()

    async def card_loss(self, ctx, player):
        if len(player['cards']) == 1:
            player['cards'].pop()
            player['isAlive'] = False
            await ctx.send(f"{player['username']} has lost their last card and is now dead!")

            with open('./data/players.json', 'r+') as f:
                players = json.load(f)
                for p in players:
                    if p['username'] == player['username']:
                        p['cards'] = player['cards']
                        p['isAlive'] = player['isAlive']
                f.seek(0)
                json.dump(players, f, indent=4)
                f.truncate()

            await self.check_winner(ctx)
            
        elif len(player['cards']) > 1:
            msg = await ctx.send(f"{player['username']} choose which card to lose by reacting with 1️⃣ or 2️⃣.")
            await msg.add_reaction('1️⃣')
            await msg.add_reaction('2️⃣')

            member = next((m for m in ctx.guild.members if m.display_name == player['username']), None)

            def check(reaction, user):
                return user == member and str(reaction.emoji) in ['1️⃣', '2️⃣']

            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            card_to_lose = int(reaction.emoji[0]) - 1
            player['cards'].pop(card_to_lose)
            await ctx.send(f"{player['username']} has lost a card.")

            with open('./data/players.json', 'r+') as f:
                players = json.load(f)
                for p in players:
                    if p['username'] == player['username']:
                        p['cards'] = player['cards']
                f.seek(0)
                json.dump(players, f, indent=4)
                f.truncate()

    @commands.command()
    async def exchange(self, ctx):
        with open('./data/players.json', 'r+') as f:
            players = json.load(f)

            for player in players:
                if player['username'] == ctx.author.display_name:

                    pl = next((p for p in players if p['username'] == ctx.author.display_name), None)

                    if pl is None:
                        await ctx.send("You are not registered in the game.")
                        return

                    if not pl['isAlive']:
                        await ctx.send("You cannot use this command because you are not alive in the game.")
                        return
                    
                    file_path = r".\images\Amb.png"
                    file = File(file_path, filename="Amb.png")

                    msg2 = await ctx.send(f"{ctx.author.display_name} is attempting to exhange cards. React with 🤚 to challenge within 5 seconds.", file = file)
                    await msg2.add_reaction('🤚')
                    def check_challenge(reaction, user):
                        return user != self.bot.user and user != ctx.author and str(reaction.emoji) == '🤚'

                    try:
                        reaction, challenger = await self.bot.wait_for('reaction_add', timeout=5.0, check=check_challenge)
                        if reaction:
                            await self.challenge(ctx, 'exchange', challenger, ctx.author) 
                            return  
                    except asyncio.TimeoutError:
                        await ctx.send("No challenge was made within the time limit.")

                    firstcard = random.sample(cardList, 1)[0]
                    secondcard = random.sample(cardList, 1)[0]

                    for card in cardList:
                        if card == firstcard or card == secondcard:
                            cardList.remove(card)
                    
                    player['cards'].append(firstcard)
                    player['cards'].append(secondcard)

                    self.cards = player['cards']

                    await ctx.author.send(self.cards)

                    msg = await ctx.author.send(f'Choose which of your cards to return to the deck')

                    await msg.add_reaction('1️⃣')
                    await msg.add_reaction('2️⃣')
                    await msg.add_reaction('3️⃣')
                    
                    if len(player['cards']) == 4:
                        await msg.add_reaction('4️⃣')
                    
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

                    msg = await ctx.author.send(f'Choose another card to return to the deck')

                    await msg.add_reaction('1️⃣')
                    await msg.add_reaction('2️⃣')
                      
                    if len(player['cards']) == 3:
                        await msg.add_reaction('3️⃣')
                    
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

                    await ctx.send(f"{player['username']} exchanged influence cards.")
                    await ctx.author.send(f"You currently have {player['cards']}")
            f.seek(0)
        
            json.dump(players, f, indent=4)
            
            f.truncate()



async def setup(bot):
    await bot.add_cog(Player(bot))
