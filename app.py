import discord
import discord.emoji
import asyncio
import time
import random
import dotenv
import os


play = ["🖐️", "✌️", "✊"]

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
        com = random.choice(play)
        if play.index(msg.content) == play.index(com):
            await msg.channel.send("{}, 平手啦智障！".format(com))
        elif play.index(msg.content) > play.index(com):
            if play.index(msg.content) == 2 and play.index (com) == 0:
                await msg.channel.send("{}, 你輸了 白癡 給我去尻尻！".format(com))
            else:
                await msg.channel.send("{}, 幹, 你是不是作弊啊！".format(com))
        else:
            if play.index(msg.content) == 0 and play.index(com) == 2:
                await msg.channel.send("{}, 幹, 你是不是作弊啊！".format(com))
            else:
                await msg.channel.send("{}, 你輸了 白癡 給我去尻尻！".format(com))

client.run(os.getenv("token"))