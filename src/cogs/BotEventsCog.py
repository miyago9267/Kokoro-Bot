from discord.ext import commands
from discord import app_commands
from homo_py import homo
from typing import Union
from . import load_cogs
import re
import discord

class BotEventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot is ready!')
        print('Name: {}'.format(self.bot.user.name))
        print('ID: {}'.format(self.bot.user.id))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.content.startswith('!hello'):
            await message.channel.send('Hello!')

        if message.content.startswith('!reloadsync'):
            await load_cogs(self.bot)
            await self.bot.tree.sync()
            await message.channel.send('reload successfully!')

        if message.content.startswith('!emojis'):
            emojis = message.guild.emojis
            if emojis:
                emoji_list = [f"\\<:{emoji.name}:{emoji.id}>" for emoji in emojis]
                await message.channel.send("\n".join(emoji_list))
            else:
                await message.channel.send("此伺服器沒有自訂表情符號。")

    @app_commands.command(name='ping', description='Ping Pong')
    async def ping(self, itr):
        await itr.response.send_message('Pong!')

    @app_commands.command(name='homo', description='惡臭數字驗證器')
    async def homo(self, itr, num: str):
        result = homo(num)
        if re.match(r'^[0-9+\-*/.()]+$', result):
            await itr.response.send_message(f"像{num}這種惡臭一定等於{result}的罷（惱。")
        else:
            await itr.response.send_message(result)

    @app_commands.command(name='help', description='功能列表')
    async def help(self, itr, group: str = None):
        embed = discord.Embed(
            title = '**可可蘿使用說明**',
            description = '**沒什麼用的功能列表**\n\n'
        )
        mora_desc = '`✊✌️🖐️` - 跟可可蘿猜拳，贏了他不會脫給你看'
        random_desc = '`[隨機用途(可選)] 隨機 <選項1> <選項2> ...` - 隨機選擇'
        choice_desc = '`/choice dinner` - 決定晚餐要吃什麼\n`/choice roulette` - 俄羅斯輪盤, 抽到子彈就被/kick出去，子彈只有一顆'
        song_desc = '`/guesssong add <歌名>` - 增加一首歌至題庫中\n`/guesssong list` - 列出現有的歌單\n`/guesssong delete <歌曲編號>` - 刪除一首歌\n`/guesssong startplay` - 開一場遊戲\n`/guesssong endplay` - 強制停止一場遊戲\n`/guesssong reveal <字母>` - 開一個字母\n`/guesssong guess <歌名>` - 直接猜歌名\n`/guesssong check` - 查看本場題目'
        mygo_desc = '`$mygo <關鍵字>` - 搜尋mygo貼圖'
        embed.add_field(name='猜拳', value=mora_desc, inline=False)
        embed.add_field(name='隨機選擇器', value=random_desc, inline=False)
        embed.add_field(name='mygo貼圖搜尋器', value=mygo_desc, inline=False)
        embed.add_field(name='/choice', value=choice_desc, inline=False)
        embed.add_field(name='/song', value=song_desc, inline=False)
        await itr.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BotEventsCog(bot))