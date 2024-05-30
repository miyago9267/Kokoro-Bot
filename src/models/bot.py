import discord.ext.commands as commands
import discord
import os
from dotenv import load_dotenv
from cogs import load_cogs

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

    async def setup(self):
        pass

    async def on_ready(self):
        await load_cogs(self)
        await self.tree.sync()

