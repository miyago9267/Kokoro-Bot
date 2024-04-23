from discord.ext import commands
from algo.search import AhoCorasick
import discord
import re, random, json, os
from pathlib import Path
import requests

class ResponseKokoro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.json_path = Path(__file__).parent.parent / 'static' / 'responce_key.json'
        self.mygo_path = Path(__file__).parent.parent / 'static' / 'mygo.json'

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author == self.bot.user:
            return

        with self.mygo_path.open('r', encoding='utf-8') as file:
            self.key_res_mp = json.load(file)

        aho_corasick = AhoCorasick(self.key_res_mp.keys())
        res = aho_corasick.search(msg.content.lower())
        if res is not {}:
            for keyword in res:
                # res_list = self.key_res_mp[keyword]['value']
                res_list = requests.get(f'http://127.0.0.1:3150/mygo/img?keyword={keyword}').json().get('urls', [])
                await self._send_text(msg, random.choice(res_list))

    async def _send_text(self, msg, responce):
        await msg.channel.send(responce)