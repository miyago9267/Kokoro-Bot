from discord import app_commands
from discord.ext import commands
from pathlib import Path
import json
import discord
import os

class RoleAdder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.message_id = [int(mid) for mid in os.getenv("ROLE_HANDLE_MES_ID", "").split(",")]
        self.emoji_to_role_path = Path(__file__).parent.parent / 'static' / 'emoji_to_role.json'
        self.emoji_to_role = {
            "<:usao:1294163540554547292>": 1294160125292052480,
            "<:MonikaPoke:1041049145051467826>": 1294166790766592013,
            "<:MonikaThumbsUp:1041049134133694494>": 1087393377747742942
        }

    @commands.command(name='role_reload')
    async def mygoreload(self, ctx):
        self.emoji_to_role = await self._load_emoji_to_role()
        await ctx.channel.send('Emoji to role 已重新載入')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id not in self.message_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return
        
        role_id = self.emoji_to_role.get(str(payload.emoji))
        if role_id is None:
            return
        
        role = guild.get_role(role_id)
        if role is None:
            return

        member = guild.get_member(payload.user_id)
        if member is not None:
            print(f"給予使用者{member.name}的{role.name}身分組")
            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.message_id not in self.message_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return
        
        role_id = self.emoji_to_role.get(str(payload.emoji))
        if role_id is None:
            return

        role = guild.get_role(role_id)
        if role is None:
            return

        member = guild.get_member(payload.user_id)
        if member is not None:
            print(f"移除使用者{member.name}的{role.name}身分組")
            await member.remove_roles(role)

    async def _load_emoji_to_role(self) -> dict:
        with self.emoji_to_role_path.open('r', encoding='utf-8') as file:
            return json.load(file)


async def setup(bot):
    await bot.add_cog(RoleAdder(bot))