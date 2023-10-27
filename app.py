import discord
import discord.emoji
import asyncio
import time
import random
import dotenv
import os
import re


play = ["✊", "✌️", "🖐️"]
text = ["平手啦智障！", "你輸了 白癡 給我去尻尻！", "幹, 你是不是作弊啊！"]

dotenv.load_dotenv()
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print("Bot is ready!")
    print("Name: {}".format(client.user.name))
    print("ID: {}".format(client.user.id))

@client.event
async def on_message(msg):
    if msg.author == client.user:
        return
    # print(msg.content, msg.author)
    if msg.content in play:
        player = play.index(msg.content)
        com = random.randint(0, 2)
        judge = (player-com+3)%3
        await msg.channel.send(f'{play[com]}')
        await msg.channel.send(f'{text[judge]}')
    if re.search(r"我想死", msg.content):
        await msg.channel.send(random.choice(["寶不要死", "7414啦"]))
    if re.search(r'隨機\s', msg.content):
        st_idx = msg.content.find('隨機 ')
        query_list = [i for i in msg.content[st_idx+3:].strip(' ').split(' ') if i != '']
        query_text = msg.content[:st_idx]
        # print(f'"{msg.content[st_idx+2:]}"','\n', query_list, '➝' ,query_text)
        await msg.reply(f'隨機 [ {" ".join(query_list)} ]\n{"" if query_text==None else query_text} ➝ **{random.choice(query_list)}**')

client.run(os.getenv("token"))