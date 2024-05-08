from discord import app_commands
from discord.ext import commands
from algo.search import AhoCorasick
import discord
import re, random, json, os
from pathlib import Path
import requests

class GuessSongGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.songsStore: dict[int, list[str]] = {} # {author_id: [songs]} 所有使用者都可以出題
        self.activeId: int = 0 # author_id (現在正在遊玩的出題者ID)
        self.activeStore: list = [] # songStore[activeId] (答案 現在正在玩的題庫)
        self.activeRevealed: list = [] # revealed: a b c (現在開出來的字元)
        self.activeGuessed: list = [] # songStore[activeId] but guessed(題目 會顯示給使用者看的)
        self.activeProblemCount: int = 0 # 現在還剩幾題沒開

    guesssong = app_commands.Group(name='guesssong', description='猜歌遊戲')

    # For Game Authorities
    @guesssong.command(name='add', description="增加一首歌至題庫中")
    @app_commands.describe(song='歌名')
    async def add(self, itr, song: str = None):
        if song is None:
            await itr.response.send_message("輸入歌名喔", ephemeral=True)
            return
        author = itr.user.id
        if author not in self.songsStore:
            self.songsStore[author] = []
        if author == self.activeId:
            await itr.response.send_message("你的題目還正在被遊玩喔", ephemeral=True)
            return
        self.songsStore[author].append(song)
        await itr.response.send_message(f"已添加: {song}", ephemeral=True)
        pass

    # For Game Authorities
    @guesssong.command(name='lists', description="列出現有的歌單")
    async def lists(self, itr):
        author = itr.user.id
        if author not in self.songsStore or self.songsStore[author] == []:
            res = "You have no songs in your list"
        else:
            res = self.formatGuessForm(self.songsStore[author])
            res = f'You have {len(self.songsStore[author])} songs in your list: {res}'
        await itr.response.send_message(res, ephemeral=True)
        pass

    # For Game Authorities
    @guesssong.command(name='delete', description="刪除一首歌")
    @app_commands.describe(id='歌曲序號')
    async def delete(self, itr, id: int = None):
        if id is None:
            await itr.response.send_message("輸入要刪除的歌曲編號喔", ephemeral=True)
            return

        author = itr.user.id

        if author not in self.songsStore:
            await itr.response.send_message("老兄你沒有出任何歌", ephemeral=True)
            return

        if id not in range(1, len(self.songsStore[author])+1):
            await itr.response.send_message("查無此號", ephemeral=True)
            return

        song = self.songsStore[author].pop(id-1)
        await itr.response.send_message(f'已刪除 {song}', ephemeral=True)
        return
        pass

    # For player
    @guesssong.command(name='guess', description="嘗試猜歌")
    @app_commands.describe(guess='歌名')
    async def guess(self, itr, guess: str = None):
        lower_store = [i.lower() for i in self.activeStore]
        if self.activeStore == [] or self.activeId < 1:
            await itr.response.send_message("老兄還沒開始遊戲喔")
            return
        if guess is None:
            await itr.response.send_message("輸入你要猜的歌", ephemeral=True)
            return
        if guess.lower() in lower_store:
            find_index = lower_store.index(guess.lower())
            self.activeGuessed[find_index] = self.activeStore[find_index]
            self.activeProblemCount -= 1
            await itr.response.send_message(f"猜對了! {guess}\n{self.formatGuessForm(self.activeGuessed)}")
            if self.activeProblemCount == 0:
                await itr.channel.send(f"本局遊戲已全部開盤完畢!")
                self.reset()
            return
        else:
            await itr.response.send_message(f"猜錯了!")
        pass

    # For player
    @guesssong.command(name='reveal', description="開一個字母")
    @app_commands.describe(letter='字元')
    async def reveal(self, itr, letter: str = None):
        if letter is None:
            await itr.response.send_message("你根本沒猜", ephemeral=True)
            return
        self.revealAlphabet(letter)
        await itr.response.send_message(f"{self.formatGuessForm(self.activeGuessed)}")
        pass

    # For game authorities
    @guesssong.command(name='startplay', description="開始新一輪遊戲")
    async def startplay(self, itr):
        if self.activeId > 0:
            await itr.response.send_message("請等待本局遊戲完結再開始喔", ephemeral=True)
            return
        author = itr.user.id
        if author not in self.songsStore:
            await itr.response.send_message("你沒有出歌喔", ephemeral=True)
            return
        self.activeId = author
        self.activeStore = self.songsStore[author]
        self.hideAll()
        self.activeRevealed = []
        self.activeProblemCount = len(self.activeStore)
        await itr.response.send_message(f"猜歌遊戲開始! \n{self.formatGuessForm(self.activeGuessed)}")
        pass

    # For authorities
    @guesssong.command(name='stopgame', description="終止遊戲")
    async def stopplay(self, itr):
        author = itr.user.id
        if self.activeId < 1:
                await itr.response.send_message("目前沒有遊戲正在進行", ephemeral=True)
                return
        if author == self.activeId:
            self.reset()
            await itr.response.send_message("出題者已手動重置遊戲")
            return
        else:
            await itr.response.send_message("這不是你的場，你沒有權限終止遊戲", ephemeral=True)
            return
        pass

    # For player
    @guesssong.command(name='check', description="檢查當前的題目")
    async def check(self, itr):
        if self.activeId < 1:
            await itr.response.send_message("目前沒有遊戲正在進行", ephemeral=True)
            return
        await itr.response.send_message(f"目前的題目: \n{self.formatGuessForm(self.activeGuessed)}")
        pass

    def formatGuessForm(self, form):
        res = ['```']
        res.append(' '.join(['revealed:'] + self.activeRevealed))
        for idx, song in enumerate(form):
            res.append(f'{idx+1}. {song}')
        res.append('```')
        return '\n'.join(res)

    def revealAlphabet(self, letter: str):
        letter = letter.lower()
        lowerStore = [i.lower() for i in self.activeStore]
        for idxi, song in enumerate(lowerStore):
            for idxj, c in enumerate(song):
                if c == letter:
                    self.activeGuessed[idxi] = self.activeGuessed[idxi][:idxj] + self.activeStore[idxi][idxj] + self.activeGuessed[idxi][idxj+1:]
        self.activeRevealed.append(letter)
        pass

    def hideAll(self):
        tmp = self.activeStore.copy()
        self.activeGuessed = []
        for item in tmp:
            res = ''
            for letter in item:
                res += ('*' if letter!=' ' else ' ')
            self.activeGuessed.append(res)
        pass

    def reset(self):
        self.activeStore = []
        self.activeRevealed = []
        self.activeGuessed = []
        self.activeProblemCount = 0
        self.songsStore[self.activeId] = []
        self.activeId = 0
        pass

async def setup(bot):
    await bot.add_cog(GuessSongGame(bot))