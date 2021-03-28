# Instrukcje
1. Sklonuj repozytorium.
```bash
git clone 'https://github.com/stabor705/chmielubot'
cd chmielubot
```
2. Zainstaluj wymagania.
```bash
pip3 install -r requirements.txt
```
3. W repozytorium znajdują się tylko obiekty [Cog](https://discordpy.readthedocs.io/en/latest/ext/commands/cogs.html). Żeby zbudować swojego chmielubota, musisz utworzyć plik **`main.py`** w którym utworzysz klienta do API discorda i podłączysz odpowiednie *Cogi*.

Przykładowa treść pliku **`main.py`**:
```python
import discord
from discord.ext import commands

import chmielubot

bot = commands.Bot("jtm ")

@bot.event
async def on_ready():
    bot.add_cog(chmielubot.Szkola())
    bot.add_cog(chmielubot.Minecraft(bot, 'server', rcon_password="123"))
    bot.add_cog(chmielubot.Zbiornik(bot, 720314254312922710))

bot.run(TOKEN)
```
gdzie TOKEN - token do bota utworzonego przez ciebie na https://discord.com/developers/

Zauważ, że *Cogi* muszą zostać dodane w funkcji *on_ready()*, aby zapewnić, że przy ich dodawaniu bot będzie już prawidłowo zainicjalizowany.

4. Od tego momentu powinieneś móc uruchomić bota
```bash
python3 main.py
```