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

        self.export_json_path = Path(__file__).parent.parent / 'static' / 'songlist.json'
        self.load_import()

    guesssong = app_commands.Group(name='guesssong', description='猜歌遊戲')

    # For debug
    @commands.command(name='songlist')
    async def songlist(self, ctx):
        content = ctx.message.content[10:]
        if content == '':
            await ctx.channel.send(f"目前的題目: \n{self.formatGuessForm(self.activeGuessed)}")
            return
        # print(self.songsStore.get(int(content)))
        try:
            if self.songsStore.get(int(content)):
                await ctx.channel.send(f"目前的題目: \n{self.formatGuessForm(self.songsStore[int(content)])}")
                return
            pass
        except:
            await ctx.channel.send(f"到底在輸入三小")
            return
        pass

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
        self.save_export()
        pass

    # For Game Authorities
    @guesssong.command(name='lists', description="列出現有的歌單")
    async def lists(self, itr):
        author = itr.user.id
        if author not in self.songsStore or self.songsStore[author] == []:
            res = "你還沒有建立歌單喔"
        else:
            res = self.formatGuessForm(self.songsStore[author])
            res = f'你有 {len(self.songsStore[author])} 首歌在清單中: {res}'
        await itr.response.send_message(res, ephemeral=True)
        pass

    # For Game Authorities
    @guesssong.command(name='delete', description="刪除題庫清單中的一首歌")
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
        self.save_export()
        return
        pass

    # For Game Authorities
    @guesssong.command(name='deleteall', description="刪除題庫清單度所有歌")
    async def delete_all(self, itr):
        author = itr.user.id
        if author not in self.songsStore:
            await itr.response.send_message("老兄你沒有出任何歌", ephemeral=True)
            return

        self.songsStore[author] = []
        await itr.response.send_message(f'已刪除全部歌曲', ephemeral=True)
        self.save_export()
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
                self.resetGame()
                self.songsStore[self.activeId] = []
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
        if letter in self.activeRevealed:
            await itr.response.send_message("這個字元已經被猜過了", ephemeral=True)
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
        self.activeGuessed = self.hideAll(self.activeStore)
        self.activeRevealed = []
        self.activeProblemCount = len(self.activeStore)
        await itr.response.send_message(f"猜歌遊戲開始! \n{self.formatGuessForm(self.activeGuessed)}")
        pass

    # For game authorities
    @guesssong.command(name='stopgame', description="終止遊戲")
    async def stopplay(self, itr):
        author = itr.user.id
        if self.activeId < 1:
                await itr.response.send_message("目前沒有遊戲正在進行", ephemeral=True)
                return
        if author == self.activeId:
            self.resetGame()
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

    # For game authorities
    @guesssong.command(name='open', description="使用暱稱或字串不完全批配時由出題者直接開題目")
    async def open(self, itr, id: int = None):
        if self.activeId < 1:
            await itr.response.send_message("目前沒有遊戲正在進行", ephemeral=True)
            return
        author = itr.user.id
        if author != self.activeId:
            await itr.response.send_message("這不是你的場，你沒有權限開題目", ephemeral=True)
            return
        if id is None:
            await itr.response.send_message("輸入要開的題目編號", ephemeral=True)
            return
        if id not in range(1, len(self.activeStore)+1):
            await itr.response.send_message("查無此號", ephemeral=True)
            return
        self.activeGuessed[id-1] = self.activeStore[id-1]
        pass

    @guesssong.command(name='preview', description="歌單編輯期間預覽題目的樣子")
    async def preview(self, itr):
        author = itr.user.id
        if author not in self.songsStore or self.songsStore[author] == []:
            res = "你還沒有建立歌單喔"
        else:
            res = self.formatGuessForm(self.hideAll(self.songsStore[author]))
            res = f'你有 {len(self.songsStore[author])} 首歌在清單中: {res}'
        await itr.response.send_message(res, ephemeral=True)
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

    def hideAll(self, store: list[str]) -> list[str]:
        tmp = []
        for item in store:
            res = ''
            for letter in item:
                res += ('*' if letter!=' ' else ' ')
            tmp.append(res)
        return tmp
        pass

    def resetGame(self):
        self.activeStore = []
        self.activeRevealed = []
        self.activeGuessed = []
        self.activeProblemCount = 0
        self.activeId = 0
        self.save_export()
        pass

    def save_export(self):
        with self.export_json_path.open('w', encoding='utf-8') as file:
            json.dump(self.songsStore, file, ensure_ascii=False, indent=4)

    def load_import(self):
        if not self.export_json_path.exists():
            return

        if self.export_json_path.stat().st_size == 0:
            return

        with self.export_json_path.open('r', encoding='utf-8') as file:
            tmp = json.load(file)
        for key, value in tmp.items():
            self.songsStore[int(key)] = value

async def setup(bot):
    await bot.add_cog(GuessSongGame(bot))