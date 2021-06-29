from .rcon import RCon
from .mcserver import McServer

import discord
from discord.ext import commands
import requests

import asyncio

class Minecraft(commands.Cog):
    """Minecraft chmielubot module. That's where actual commands reside."""

    def __init__(self, bot, server_dir, memory=1024, rcon_password=""):
        """
        Parameters:
        server_dir : str
            Directory in which your all your server files reside. More precisely, directory in which server.jar file resides.
        rcon_password : str
            Password to remote control of your server.
        """
        self.server = McServer(server_dir, memory)
        self.bot = bot
        self.rcon = None
        self.log_channel = None
        self.rcon_password = rcon_password

    async def start_server(self):
        await self.server.run()
        self.log_channel = await self.bot.fetch_channel(802263842397880401)
        self.bot.loop.create_task(self.broadcast_logs())
        self.bot.loop.create_task(self.check_for_players())

    async def stop_server(self):
        await self.server.stop()
        await self.bot.change_presence()
        self.rcon = None

    async def broadcast_logs(self):
        while self.server.process:
            line = await self.server.process.stdout.readline()
            if line:
                await self.log_channel.send("```" + line.decode('ascii') + "```")
            else:
                await asyncio.sleep(1)

    async def check_for_players(self):
        counter = 0
        while True:
            await asyncio.sleep(60)
            players = self.query_players()
            if players is None:
                continue
            if len(players) == 0:
                counter += 1
                if counter >= 60:
                    await self.stop_server()
                    return await self.log_channel.send("``` Serwer został zatrzymany ze względu na brak aktywności graczy. Jeśli chcesz włączyć serwer z powrotem użyj komendy jtm server_start ```")
            else:
                counter = 0
            await self.bot.change_presence(activity=discord.Game(f"Minecraft z {len(players)} osobami."))

    def query_players(self):
        output = self.send_rcon_command("/list")
        if output is None:
            return None
        output = output.split(":")[1]
        output = output[1:]
        if not output:
            return list()
        players = output.split(", ")
        return players

    def send_rcon_command(self, command):
        if self.rcon is None and not self.set_rcon():
            return None
        return self.rcon.send_command(command)

    def set_rcon(self):
        try:
            self.rcon = RCon("127.0.0.1", 25575, self.rcon_password)
        except Exception:
            return False
        return True

    @commands.command(name="server_command")
    @commands.is_owner()
    async def server_command(self, ctx, command):
        output = self.send_rcon_command(command)
        if output is None:
            return await ctx.send("Nie udało się wysłać komendy. Czy na pewno rcon aktualnie funkcjonuje na serwerze?")
        if output:
            await ctx.send('```' + output + '```')

    @commands.command(name="server_status")
    async def server_status(self, ctx):
        players = self.query_players()
        if players is None:
            return await ctx.send("Serwer jest aktualnie wyłączony.")
        res = f"``` Aktualnie na serwerze znajduje się {len(players)} osób.\n"
        for idx, player in enumerate(players):
            res += f"{idx + 1}. {player}\n"
        res += "```"
        await ctx.send(res)

    @commands.command(name="server_start")
    async def server_start(self, ctx):
        if self.server.is_up():
            return await ctx.send("Serwer już jest uruchomiony.")
        await ctx.send("Załączam serwer...")
        await self.start_server()

    @commands.command(name="server_stop")
    @commands.is_owner()
    async def server_stop(self, ctx):
        if not self.server.is_up():
            return await ctx.send("Serwer jest już wyłączony.")
        await ctx.send("Wyłączam serwer...")
        await self.stop_server()
