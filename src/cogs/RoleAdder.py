from discord.ext import commands
from pathlib import Path
from config import global_config, reload_global_config
import json
import os

class RoleAdder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.message_id = global_config.get("RoleAdd", {})

    @commands.command(name='role_reload')
    async def emoji_to_role_reload(self, ctx):
        await self._load_emoji_to_role()
        await ctx.channel.send('Emoji to role 已重新載入')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        emoji_to_role = global_config.get("RoleAdd", {}).get(str(payload.message_id), {})
        if emoji_to_role is {}:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return
        
        role_id = emoji_to_role.get(str(payload.emoji))
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
        emoji_to_role = global_config.get("RoleAdd", {}).get(str(payload.message_id), {})
        if emoji_to_role is {}:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return
        
        role_id = emoji_to_role.get(str(payload.emoji))
        if role_id is None:
            return

        role = guild.get_role(role_id)
        if role is None:
            return

        member = guild.get_member(payload.user_id)
        if member is not None:
            print(f"移除使用者{member.name}的{role.name}身分組")
            await member.remove_roles(role)

    async def _load_emoji_to_role(self) -> None:
        reload_global_config()
        return


async def setup(bot):
    await bot.add_cog(RoleAdder(bot))