from discord.ext import commands
import discord
import re, random

class Notify(commands.cog):
    def __init__(self, bot):
        self.bot = bot