from discord.ext import commands
import requests
from bs4 import BeautifulSoup
from datetime import date
import time
import random

class Szkola(commands.Cog):
    classes = {
        "4i2": "4i2"
    }
    days = [
        "Poniedziałek",
        "Wtorek",
        "Środa",
        "Czwartek",
        "Piątek"
    ]

    @commands.command(name="plan")
    async def plan(self, ctx, *, day=None, school_class="4i2"):
        BASE = 'http://zs5.elk.pl/plan/'
        LIST = 'http://zs5.elk.pl/plan/lista.html'

        if day is None: day = date.today().weekday()
        else:
            try:
                day = int(day) - 1
            except ValueError:
                return
        if day < 0 or day > 6:
            return await ctx.send(f"Dzień {day} nie jest poprawną formą dnia")
        if day > 4 and day < 7:
            day = 0
        school_class = self.classes.get(school_class.lower())
        if not school_class:
            return await ctx.send(f"Podana klasa {school_class} jest nieprawidłową klasą.")

        # it works
        r = requests.get(LIST)
        r.encoding = 'utf-8'
        doc = BeautifulSoup(r.text)
        plan_tag = doc.find(lambda tag: tag.text == school_class)
        plan_relative_url = plan_tag.find("a")["href"]
        plan_url = BASE + plan_relative_url

        r = requests.get(plan_url)
        r.encoding = 'utf-8'
        doc = BeautifulSoup(r.text)
        table = doc.find_all('table', limit=3)[2]
        table_rows = table.find_all('tr')[1:]
        entries = list()
        hours = list()
        for table_row in table_rows:
            hour = table_row.find_all('td')[1]
            lesson = table_row.find_all('td')[day + 2]
            hour = hour.text.replace(" ", "")
            hours.append(hour)
            parts = lesson.find_all(class_='p n s'.split())
            groups = [parts[x*3:x*3+3] for x in range(len(parts) // 3)]
            entry = tuple(' '.join([part.text.strip() for part in group]) for group in groups)
            if not entry:
                entry = tuple(" ")
            entries.append(entry)
        max_line_length = max([len(entry[0]) + len(hour) + 5 for entry, hour in zip(entries, hours)])
        stars_length = (max_line_length - len(self.days[day])) // 2
        res = "-" * stars_length + self.days[day] + "-" * stars_length + "\n"
        for idx, hour, entry in zip(range(len(entries)), hours, entries):
            line = f"{idx + 1}. {hour} {entry[0]}\n"
            res += line
            if len(entry) > 1:
                res += " " * (len(line) - len(entry[0]) - 1) + entry[1] + "\n"
        prefix = random.choice(["elm", "excel", "python", "vim", "v"])
        await ctx.send(f"```{prefix}\n" + res + "```")

    @commands.command(name="matura", help="Pokazuje, ile dni pozostalo do matury")
    async def matura(self, ctx):
       exam = date(2021, 5, 4)
       school_end = date(2021, 4, 30)
       today = date.today()
       time1 = (exam - today)
       time2 = (school_end - today)
       await ctx.send(f"```css\nDo końca roku szkolnego pozostało: {time2.days} dni\nDo matury pozostało: {time1.days} dni```")
