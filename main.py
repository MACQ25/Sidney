import discord
from discord.ext import commands
import os
#from help_cog import help_cog}

description = "This is Sidney bot's description, make sure to write something relevant here later"

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

print("hewwo github")

sidneyBot = commands.Bot(command_prefix='!',
                         description=description,s
                         intents=intents)


@sidneyBot.event
async def on_ready():
  print(sidneyBot.get_command("add2"))
  print(f'{sidneyBot.user} says: God save the queen!')


@sidneyBot.event
async def on_message(msg):
  if msg.author != sidneyBot.user:
    print(f'{msg.author}: {msg.content}')


@sidneyBot.command("salute")
async def salute(ctx, usr):
  await ctx.send(f'cheers {usr}')

@sidneyBot.command("add")
async def add(ctx, left: int, right: int):
  print("add")
  await ctx.send(left + right)


sidneyBot.run(os.environ['myToken'])

# sauce for async kerfuffle solu: https://stackoverflow.com/questions/71504627/runtimewarning-coroutine-botbase-load-extension-was-never-awaited-after-upd

# Need to add the command cog to the CLIENT as said: https://stackoverflow.com/questions/71960548/bot-launches-fine-but-the-commands-do-not-work?rq=3
