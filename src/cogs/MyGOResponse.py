from discord.ext import commands
from algo.search import AhoCorasick
import discord
import re, random, json, os
from pathlib import Path
import requests

class MyGOResponse(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ignore_channels = [1011948815391137832]

        self.mygo_path = Path(__file__).parent.parent / 'static' / 'mygo.json'
        self.key_res_mp = {}


    @commands.command(name='mygo')
    async def mygo(self, ctx):
        msg = ctx.message
        responce = await self._fetch_responce(msg.content[6:])
        if len(responce) and responce is not None:
            await self._send_text(msg, responce)
        else:
            await msg.channel.send('查無此圖')
            await self._send_text(msg, await self._fetch_responce('找不到'))

    @commands.command(name='mygoreload')
    async def mygoreload(self, ctx):
        await self._load_responce()
        await self._send_text(ctx.message, 'mygo response reload successfully!')

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author == self.bot.user:
            return

        if msg.content[:6] == '$mygo ':
            return

        if msg.content[:11] == '$mygoreload':
            return

        if msg.channel in self.ignore_channels:
            print('ignore channel')
            return

        query_key = await self._check_keyword(msg)
        if query_key is not None:
            responce = await self._fetch_responce(query_key)
            await self._send_text(msg, responce)

    async def _check_keyword(self, msg) -> str:
        if self.key_res_mp == {}:
            self.key_res_mp = await self._load_response()

        aho_corasick = AhoCorasick(self.key_res_mp.keys())
        res = aho_corasick.search(msg.content.lower())
        if res is not {}:
            for keyword in res:
                res_list = self.key_res_mp[keyword]['value']
                return random.choice(res_list)
        return None

    async def _fetch_responce(self, query_key) -> list:
        request_url = f'https://mygoapi.miyago9267.com/mygo/img?keyword={query_key}'
        res_list = requests.get(request_url).json().get('urls', [])
        return random.choice(res_list).get('url') if res_list else []

    async def _load_response(self) -> dict:
        with self.mygo_path.open('r', encoding='utf-8') as file:
            return json.load(file)

    async def _send_text(self, msg, responce) -> None:
        await msg.channel.send(responce)

async def setup(bot):
    await bot.add_cog(MyGOResponse(bot))