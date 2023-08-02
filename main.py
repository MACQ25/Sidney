import discord
from discord import voice_client
from discord.ext import commands
import os
import asyncio
import youtube_dl

# from help_cog import help_cog}

description = "This is Sidney bot's description, make sure to write something relevant here later"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

sidneyBot = discord.Bot(
    command_prefix=commands.when_mentioned_or('/'),
    description=description,
    intents=intents,
    debug_guilds=[1124124038634156062]
)


@sidneyBot.event
async def on_ready():
    print(sidneyBot.get_command("add"))
    print(f'{sidneyBot.user} says: God save the queen!')


@sidneyBot.command(description="Say Hi to another user on the server")
async def salute(ctx, msg):
    await ctx.respond(f'cheers {msg}')


@sidneyBot.command()
async def add(ctx, left: int, right: int):
    print("add")
    await ctx.respond(str(left + right))


@sidneyBot.command(name='join', description='Tells the bot to join the voice channel')
async def join(ctx, *, channel: discord.VoiceChannel):
    if not ctx.author.voice:
        await ctx.respond("{} is not connected to a voice channel".format(ctx.author.name))
    else:
        if ctx.voice_client is None:
            await ctx.respond("cheers m8")
            await channel.connect()
        else:
            await ctx.respond("Already in a channel m8")


@sidneyBot.command(name='leave', description='Tells the bot to leave the voice channel')
async def leave(com):
    if com.voice_client is None:
        await com.respond("I ain't in a channel ya piker!")
    else:
        if com.voice_client.channel is not com.author.voice.channel:
            await com.respond("You ain't in my channel ya no-hoper!")
        else:
            await com.voice_client.disconnect(force=True)
            await com.respond("done")

sidneyBot.run('MTEyNDEyMDgyNDI0NTM5MTQzNA.GwhfIv.jlGfuQGs3vRk2xCM2xZWAfZvAtRZ-ac1Kg-Blc')

# sauce for async kerfuffle solu: https://stackoverflow.com/questions/71504627/runtimewarning-coroutine-botbase-load-extension-was-never-awaited-after-upd

# Need to add the command cog to the CLIENT as said: https://stackoverflow.com/questions/71960548/bot-launches-fine-but-the-commands-do-not-work?rq=3
