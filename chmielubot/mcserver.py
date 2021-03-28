import asyncio
import subprocess

import time
import os

class McServer:
    """Class used for interfacing with minecraft server process"""
    def __init__(self, server_dir, memory=1024):
        """Note that it does not start the server. You have to call run() method after creating McServer object."""
        self.process = None
        self.server_dir = server_dir
        self.memory = memory

    async def run(self):
        last_cwd = os.getcwd()
        os.chdir(self.server_dir)
        self.process = await asyncio.create_subprocess_exec("java", f"-Xmx{self.memory}M", f"-Xms{self.memory}M", "-jar", "server.jar", "nogui", stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        os.chdir(last_cwd)

    async def stop(self):
        self.send_command("/stop")
        await self.process.wait()
        self.process = None

    def send_command(self, command, *args):
        if self.process is None:
            return
        msg = command
        if args:
            msg += " " + " ".join(args)
        msg += "\n"
        data = msg.encode('ascii')
        self.process.stdin.write(data)

    def is_up(self):
        return self.process is not None