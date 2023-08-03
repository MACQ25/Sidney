import discord
from discord import voice_client
from discord.ext import commands
import os
import asyncio

# from help_cog import help_cog}

description = "This is Sidney bot's description, make sure to write something relevant here later"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

sidneyBot = commands.Bot(
    command_prefix=commands.when_mentioned_or('/'),
    description=description,
    intents=intents,
    debug_guilds=[1124124038634156062]
)


@sidneyBot.event
async def on_ready():
    print(f'{sidneyBot.user} says: God save the queen!')


@sidneyBot.slash_command(description="Say Hi to another user on the server")
async def salute(ctx, msg):
    await ctx.respond(f'cheers {msg}')


@sidneyBot.slash_command()
async def add(ctx, left: int, right: int):
    await ctx.respond(str(left + right))


for res in os.listdir("cogs"):
    if res.endswith(".py"):
        sidneyBot.load_extension(f'cogs.{res.replace(".py", "")}')

sidneyBot.run('MTEyNDEyMDgyNDI0NTM5MTQzNA.GwhfIv.jlGfuQGs3vRk2xCM2xZWAfZvAtRZ-ac1Kg-Blc')



# Sources, some good, some unused:

# sauce for async kerfuffle solu: https://stackoverflow.com/questions/71504627/runtimewarning-coroutine-botbase-load-extension-was-never-awaited-after-upd

# Need to add the command cog to the CLIENT as said: https://stackoverflow.com/questions/71960548/bot-launches-fine-but-the-commands-do-not-work?rq=3

# Kind gentleman that helped explain why "load_extension()" and "setup()" were not working
# changed sidney = discord.Bot() to sidney = commands.Bot() as commands and support cogs and discord doesnt
# sauce: https://stackoverflow.com/questions/71369200/pycord-error-discord-errors-extensionfailed-extension-cogs-cmds-raised-an-er
