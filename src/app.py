from dotenv import load_dotenv
import os
from models.bot import Bot

load_dotenv()

def bot_start():
    bot = Bot()
    bot.run(os.getenv('BOT_TOKEN'))

if __name__=='__main__':
    bot_start()
