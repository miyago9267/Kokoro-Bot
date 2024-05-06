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

    @commands.command(name='mygo')
    async def mygo(self, ctx):
        msg = ctx.message
        responce = await self._fetch_responce(msg.content[6:])
        if len(responce) and responce is not None:
            await self._send_text(msg, responce)
        else:
            await msg.channel.send('查無此圖')
            await self._send_text(msg, await self._fetch_responce('找不到'))


    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author == self.bot.user:
            return

        return

        query_key = await self._check_keyword(msg)
        if query_key is not None:
            responce = await self._fetch_responce(query_key)
            await self._send_text(msg, responce)

    async def _check_keyword(self, msg) -> str:
        with self.mygo_path.open('r', encoding='utf-8') as file:
            self.key_res_mp = json.load(file)

        aho_corasick = AhoCorasick(self.key_res_mp.keys())
        res = aho_corasick.search(msg.content.lower())
        if res is not {}:
            for keyword in res:
                res_list = self.key_res_mp[keyword]['value']
                return random.choice(res_list)
        return None

    async def _fetch_responce(self, query_key) -> list:
        request_url = f'http://127.0.0.1:3150/mygo/img?keyword={query_key}'
        res_list = requests.get(request_url).json().get('urls', [])
        return random.choice(res_list) if res_list else []


    async def _send_text(self, msg, responce) -> None:
        await msg.channel.send(responce)