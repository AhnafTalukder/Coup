import random
import settings
import discord 
from discord.ext import commands
from cogs.Player import Player
from cogs.Gameplay import Gameplay
    
logger = settings.logging.getLogger("bot")



    
def run():
    intents = discord.Intents.all()
    intents.message_content = True
    
    bot = commands.Bot(command_prefix="!", intents=intents)
    
    @bot.event 
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")
        await bot.load_extension("cogs.Player")
        await bot.load_extension("cogs.Gameplay")
        
    bot.run(settings.DISCORD_API_SECRET, root_logger=True)

if __name__ == "__main__":
    run()