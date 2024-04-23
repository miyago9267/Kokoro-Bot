from discord.ext import commands
from algo.search import AhoCorasick
import discord
import re, random, json, os
from pathlib import Path

class ResponseKokoro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.json_path = Path(__file__).parent.parent / 'static' / 'responce_key.json'

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author == self.bot.user:
            return

        with self.json_path.open('r', encoding='utf-8') as file:
            self.key_res_mp = json.load(file)

        aho_corasick = AhoCorasick(self.key_res_mp.keys())
        res = aho_corasick.search(msg.content.lower())
        if res is not {}:
            for keyword in res:
                res_list = self.key_res_mp[keyword]['value']
                await self._send_text(msg, random.choice(res_list))

    async def _send_text(self, msg, responce):
        await msg.channel.send(responce)