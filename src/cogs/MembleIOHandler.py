from discord import app_commands
from discord.ext import commands
import discord

class MembleIOHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        system_channel = member.guild.system_channel
        if system_channel:
            await system_channel.send(f"歡迎回來，{member.mention}主人！")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        system_channel = member.guild.system_channel
        if system_channel:
            await system_channel.send(f"{member.mention}大人離開我們了...")

async def setup(bot):
    await bot.add_cog(MembleIOHandler(bot))