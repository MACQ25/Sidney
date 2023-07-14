import discord
import os
import ffmpeg
import asyncio
from discord.ext import commands
from cogs.music_cog import music_cog
#from help_cog import help_cog

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='%', intents=intents)

@bot.event
async def on_ready():
  await bot.add_cog(music_cog(bot))
  muhCog = bot.get_cog('music_cog')
  command2 = muhCog.get_commands()
  print([c.name for c in command2])
  print('{0.user} says: God save the queen!'.format(bot))


@bot.event
async def on_message(message):

  #This is for debbugging purposes
  username = str(message.author)
  user_message = str(message.content)
  channel = str(message.channel)

  print(f"{username} said: '{user_message}' ({channel})")
  # debug ends here

  if message.author == bot.user:
    return
  if message.content == "$hello":
    await message.channel.send("evening")

async def main():
  await bot.start(os.environ['myToken'])
  bot.run(os.environ['myToken'], root_logger=True)


asyncio.run(main())

# sauce for async kerfuffle solu: https://stackoverflow.com/questions/71504627/runtimewarning-coroutine-botbase-load-extension-was-never-awaited-after-upd

# Need to add the command cog to the CLIENT as said: https://stackoverflow.com/questions/71960548/bot-launches-fine-but-the-commands-do-not-work?rq=3
