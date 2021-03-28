import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import requests
import asyncio
import random
import os.path

class Streamer:
    def __init__(self, name):
        self.name = name
        self.is_streaming = False

    @property
    def url(self):
        return f"https://zbiornik.tv/{self.name}"

    def __str__(self):
        return self.name



class Zbiornik(commands.Cog):
    def __init__(self, bot, zbiornik_channel_id):
        """
        Parameters:
        ----------
        zbiornik_channel_id : int
            Id of channel where ChmieluBot should broadcast announcements to.
        """
        self.bot = bot
        try:
            streamer_names = open('streamers').read().splitlines()
        except FileNotFoundError:
            streamer_names = list()
        self.streamers = [Streamer(streamer_name) for streamer_name in streamer_names]
        self.zbiornik_channel_id = zbiornik_channel_id

    @staticmethod
    def zbiornik_request(relative_url):
        BASE = "https://zbiornik.tv"

        url = BASE + '/' + relative_url
        r = requests.get(url)
        document = BeautifulSoup(r.text)
        gate = document.find('a')["href"]
        url = BASE + gate
        r = requests.get(url)
        return r

    @staticmethod
    def is_streaming(streamer):
        document = BeautifulSoup(Zbiornik.zbiornik_request(streamer.name).text)
        return not document.find(id="video0Holder")
    
    def get_streamer_by_name(self, name):
        for streamer in self.streamers:
            if streamer.name == name:
                return streamer
        return None

    def get_streaming_streamers(self):
        return [streamer for streamer in self.streamers if self.is_streaming(streamer)]
            

    def write_to_database(self):
        open("streamers", "w").write('\n'.join([streamer.name for streamer in self.streamers]))


    async def check_on_streamers(self):
        MIN_TTS, MAX_TTS = (10 * 60, 60 * 60)
        channel = self.bot.get_channel(self.zbiornik_channel_id)

        while True:
            for streamer in self.streamers:
                embed = discord.Embed(
                    title=streamer.name,
                    url=streamer.url,
                    colour=discord.Colour.purple(),
                )
                if self.is_streaming(streamer):
                    if not streamer.is_streaming:
                        streamer.is_streaming = True
                        embed.description = f"{streamer.name} prowadzi teraz transmisję na żywo. Sprawdź na {streamer.url}"
                        await channel.send(embed=embed)
                else:
                    if streamer.is_streaming:
                        streamer.is_streaming = False
                        embed.description = f"Transmisja u {streamer.name} została zakończona."
                        await channel.send(embed=embed)
            tts = random.randint(MIN_TTS, MAX_TTS)
            await asyncio.sleep(tts)
    
    @commands.command(name="zbiornik_add")
    async def zbiornik_add(self, ctx, user):
        document = BeautifulSoup(self.zbiornik_request(user).text)
        if not document.find(id="mainStream"):
            return await ctx.send(f"Użytkownik {user} nie istnieje.")
        streamer_names = [streamer.name for streamer in self.streamers]
        if user in streamer_names:
            return await ctx.send(f"Użytkownik {user} już jest w bazie.")
        self.streamers.append(Streamer(user))
        self.write_to_database()
        await ctx.send(f"Użytkownik {user} został pomyślnie dodany do bazy.")
    
    @commands.command(name="zbiornik_list")
    async def zbiornik_list(self, ctx):
        res = "```\nUżytkownicy znajdujący się aktualnie w bazie:\n"
        for idx, streamer in enumerate(self.streamers):
            res += f"{idx + 1}. {streamer}\n"
        res += "```"
        await ctx.send(res)
    
    @commands.command(name="zbiornik_del")
    async def zbiornik_del(self, ctx, user):
        for idx, streamer in enumerate(self.streamers):
            if streamer.name == user:
                del self.streamers[idx]
                await ctx.send(f"Użytkownik {user} został pomyślnie usunięty.")
                break
        else:
            ctx.send(f"Użytkownika {user} nie znajduje się w bazie.")
        self.write_to_database()

    @commands.command(name="zbiornik_status")
    async def zbiornik_status(self, ctx, user):
        streamer = self.get_streamer_by_name(user)
        if streamer is None:
            return await ctx.send(f"Użytkownika {user} nie ma w bazie.")

        embed = discord.Embed(
            title=streamer.name,
            url=streamer.url,
            colour=discord.Colour.purple(),
        )
        if self.is_streaming(streamer):
            embed.description = f"{streamer.name} prowadzi teraz transmisję na żywo. 🔴"
        else:
            embed.description = f"{streamer.name} nie prowadzi aktualnie transmisji na żywo."
        await ctx.send(embed=embed)
    
    @commands.command(name="zbiornik_streams")
    async def zbiornik_streams(self, ctx):
        streamers = self.get_streaming_streamers()
        if len(streamers) == 0:
            return await ctx.send("Nikt nie prowadzi teraz transmisji. ;- (")
        for streamer in streamers:
            embed = discord.Embed(
                title=streamer.name,
                url=streamer.url,
                colour=discord.Colour.purple(),
                description=f"{streamer.name} prowadzi teraz transmisję na żywo. 🔴"
            )
            await ctx.send(embed=embed)