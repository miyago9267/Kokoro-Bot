import discord
import discord.emoji
import asyncio
import time
import random
import dotenv
import os


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
        await msg.channel.send(f'{play[com]}, {text[judge]}')

client.run(os.getenv("token"))
