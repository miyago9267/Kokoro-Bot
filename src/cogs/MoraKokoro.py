from discord import app_commands
from discord.ext import commands
import discord
import re, random

class MoraKokoro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.play = ["✊", "✌️", "🖐️"]
        self.text = ["平手！", "你輸了！雜魚雜魚", "幹, 你是不是作弊啊！"]

    choice = app_commands.Group(name='choice', description='隨機選擇器')

    @commands.command(name='help')
    async def help(self, ctx):
        embed = discord.Embed(
            title = '**可可蘿使用說明**',
            description = '**沒什麼用的功能列表**\n\n'
        )
        mora_desc = '`✊✌️🖐️` - 跟可可蘿猜拳，贏了他不會脫給你看'
        random_desc = '`[隨機用途(可選)] 隨機 <選項1> <選項2> ...` - 隨機選擇'
        embed.add_field(name='猜拳', value=mora_desc, inline=False)
        embed.add_field(name='隨機選擇器', value=random_desc, inline=False)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author == self.bot.user:
            return

        if msg.content in self.play:
            await self._mora(msg)

        if re.search(r'隨機\s', msg.content):
            await self._send_response(msg, self._random_choice(msg.author.id, msg.content))

    @choice.command(name='dinner', description='決定晚餐要吃什麼')
    @app_commands.describe(choice='備選選項 沒靈感可以用預設的')
    async def choice_dinner(self, itr, choice: str = None):
        if choice == '一中':
            choices = [
                '小象', '雲居', '丸勝', '漁藏', '山西刀削麵', '拓海家', 'すきや', '麥當勞', '火鍋', '就醬拌'
            ]
        elif choice:
            choices = choice.split(' ')
        else:
            choices = ['火鍋','壽司','鐵板燒','鍋燒','水餃','炒飯','拉麵','麵攤','便當','超商']
        await itr.response.send_message(f"{self._random_choice(itr.user.id , '隨機 ' + ' '.join(choices), '晚餐列表')}", ephemeral=True)

    @choice.command(name='roulette', description='俄羅斯輪盤, 抽到子彈就被踢出去，子彈只有一顆')
    @app_commands.describe(bullets='彈巢容量, 當中有一個會是子彈')
    async def choice_roulette(self, itr, bullets: int = 1):
        if bullets < 1:
            await itr.response.send_message('彈巢空間至少要有一顆子彈', ephemeral=True)
            return
        choices = ['空' for i in range(bullets-1)] + ['子彈']
        res = self._random_choice(itr.user.id, '隨機 '+' '.join(choices))
        await itr.response.send_message(res)

    async def _mora(self, msg):
        player = self.play.index(msg.content)
        com = random.randint(0, 2)
        judge = (player-com+3)%3
        await msg.channel.send(f'{self.play[com]}')
        await msg.channel.send(f'{self.text[judge]}')

    def _random_choice(self, author: int, msg: str, choice:str = None) -> str:
        random_query = msg.replace('\n', ' ')

        st_idx = random_query.find('隨機 ')
        query_list = [i for i in random_query[st_idx+3:].strip(' ').split(' ') if i != '']
        query_text = random_query[:st_idx] if choice == None else choice
        if author == self.bot.owner_id and '還沒死透' in query_list:
            return f'隨機 [ {" ".join(query_list)} ]\n{"" if query_text==None else query_text} ➝ **還沒死透**'
        else:
            return f'隨機 [ {" ".join(query_list)} ]\n{"" if query_text==None else query_text} ➝ **{random.choice(query_list)}**'

    async def _send_response(self, ctx, msg):
        await ctx.reply(msg)

async def setup(bot):
    await bot.add_cog(MoraKokoro(bot))