from discord.ext import commands
import discord
import re
import time
import datetime

class Utility(commands.Cog):

    @commands.command(name="emojify", help="Zamiana znakow alfanumerycznych na emoji")
    async def emojify(self, ctx, *args):

        #My code look like a shit,
        #Optimization and my english skills sucks
        #But it should work
        
        args = " ".join(args).casefold()
        if len(args) > 90:
            await ctx.send("Tekst przekracza 90 znakow!")
            return

        try:
            await ctx.message.delete()
        except discord.Forbidden:
            await ctx.send(f"Nie można usunąć wiadomości {ctx.author.name}: Brak wymaganych uprawnien.")
    
        numbers = {
            '1':':one:',
            '2':':two:',
            '3':':three:',
            '4':':four:',
            '5':':five:',
            '6':':six:',
            '7':':seven:',
            '8':':eight:',
            '9':':nine:',
            '0':':zero:',
        }
        symbols = {
            '?':':question:',
            '!':':exclamation:',
            '#': ':hash:',
            '*': ':asterisk:'

        }
        output = ""
        for s in args:
            if re.search("[a-z]", s):
                output += f":regional_indicator_{s}:"
            elif re.search("\d", s):
                output += numbers[s]
            elif re.search("\s", s):
                output += " "
            elif symbols.get(s):
                output += symbols.get(s)
            else:
                output += ":x:"

        await ctx.send(output)
        
    @commands.command(name="matura", help="Pokazuje, ile dni pozostalo do matury")
    async def matura(self, ctx):
       exam = datetime.datetime(2021, 5, 4, 9)
       school_end = datetime.datetime(2021, 4, 30, 9)
       today = exam.today()
       time1 = (exam - today)
       time2 = (school_end - today)
       await ctx.send(f"```css\nDo końca roku szkolnego pozostało: {time2.days} dni\nDo matury pozostało: {time1.days} dni```")
