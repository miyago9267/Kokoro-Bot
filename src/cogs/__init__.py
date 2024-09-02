import os
import importlib
from discord.ext import commands

async def load_cogs(bot):
    cog_directory = "src/cogs"
    for filename in os.listdir(cog_directory):
        if filename.endswith(".py") and filename != "__init__.py":
            await bot.load_extension(f"cogs.{filename[:-3]}")