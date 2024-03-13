import discord.ext.commands as commands
import discord
import os
from dotenv import load_dotenv
from src.cogs.mora import MoraKokoro

load_dotenv()

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=os.getenv('COMMAND_PREFIX'),
            intents=intents,
            help_command=None
        )
        self.owner_id = int(os.getenv('OWNER_ID'))

    async def on_ready(self):
        await self.add_cog(BotEventsCog(self))
        await self.add_cog(MoraKokoro(self))

class BotEventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot is ready!')
        print('Name: {}'.format(self.bot.user.name))
        print('ID: {}'.format(self.bot.user.id))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if message.content.startswith('!hello'):
            await message.channel.send('Hello!')