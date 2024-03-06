from discord.ext import commands
import discord
import re, random

class MoraKokoro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.play = ["✊", "✌️", "🖐️"]
        self.text = ["平手！", "你輸了！雜魚雜魚", "幹, 你是不是作弊啊！"]

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
        # print(msg.content, msg.author)

        if msg.content in self.play:
            player = self.play.index(msg.content)
            com = random.randint(0, 2)
            judge = (player-com+3)%3
            await msg.channel.send(f'{self.play[com]}')
            await msg.channel.send(f'{self.text[judge]}')

        if re.search(r'隨機\s', msg.content):
            random_query = msg.content.replace('\n', ' ')

            st_idx = random_query.find('隨機 ')
            query_list = [i for i in random_query[st_idx+3:].strip(' ').split(' ') if i != '']
            query_text = random_query[:st_idx]
            await msg.reply(f'隨機 [ {" ".join(query_list)} ]\n{"" if query_text==None else query_text} ➝ **{random.choice(query_list)}**')
