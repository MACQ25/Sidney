import discord
from discord import voice_client, Client
from discord.ext import commands
from discord import Guild
import os
import asyncio
import demoji

# from help_cog import help_cog}

description = "This is Sidney bot's description, make sure to write something relevant here later"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

sidneyBot = commands.Bot(
    command_prefix=commands.when_mentioned_or('/'),
    description=description,
    intents=intents,
    debug_guilds=[1124124038634156062, 708200173926481920]
)


def struct(guild):
    newEnt = {
        guild.id: {
            "CurrentlyPlaying": None,
            "playlist": None,
            "Qn": 0,
        }
    }
    return newEnt


class ClientsData:
    serverStatus = {}

    @classmethod
    async def dataBuilder(cls):
        async for guild in sidneyBot.fetch_guilds():
            cls.serverStatus.update(struct(guild))

    @classmethod
    def newEntry(cls, guild):
        cls.serverStatus.update(struct(guild))

    @classmethod
    def retrieve(cls, gId, key):
        if gId in cls.serverStatus and key in cls.serverStatus.get(gId):
            return cls.serverStatus.get(gId).get(key)

    @classmethod
    def set(cls, gId, *keys: []):
        if gId in cls.serverStatus:
            for pair in keys:
                if pair[0] in cls.serverStatus.get(gId):
                    cls.serverStatus.get(gId).update({pair[0]: pair[1]})
                else:
                    print("not here")
        else:
            print("not dict")


@sidneyBot.event
async def on_ready():
    await ClientsData.dataBuilder()
    # print(ClientsData.serverStatus) debugger to check number of servers this is in
    print(f'{sidneyBot.user} says: God save the queen!')


@sidneyBot.event
async def on_guild_join(guild: discord.Guild):
    ClientsData.newEntry(guild)
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            if demoji.replace(channel.name.lower().strip(), "").find("general") != -1:
                print("FOUND IT:" + channel.name)
                await channel.send("What's up ya wankers!")
                return
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send("What's up ya wankers!")
            return


@sidneyBot.event
async def on_guild_remove(guild: discord.Guild):
    ClientsData.serverStatus.pop(guild.id)


for res in os.listdir("cogs"):
    if res.endswith(".py"):
        sidneyBot.load_extension(f'cogs.{res.replace(".py", "")}')

sidneyBot.run('')

# Sources, some good, some unused:

# sauce for async kerfuffle solu: https://stackoverflow.com/questions/71504627/runtimewarning-coroutine-botbase-load-extension-was-never-awaited-after-upd

# Need to add the command cog to the CLIENT as said: https://stackoverflow.com/questions/71960548/bot-launches-fine-but-the-commands-do-not-w/ork?rq=3

# Kind gentleman that helped explain why "load_extension()" and "setup()" were not working
# changed sidney = discord.Bot() to sidney = commands.Bot() as commands and support cogs and discord doesnt
# sauce: https://stackoverflow.com/questions/71369200/pycord-error-discord-errors-extensionfailed-extension-cogs-cmds-raised-an-er


# YT-DLP build used, gotta check in their discord wether they can help with audio quality:
# https://github.com/yt-dlp/yt-dlp
