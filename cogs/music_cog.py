import discord
from discord.ext import commands
from youtube_dl import YoutubeDL


class music_cog(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def hello(self, ctx, *, member:discord.member):
    await ctx.send(f"hello{member.name}")
  #@commands.command(name='join',
  #                        help='Tells the bot to join the voice channel')
  #async def join(self, com: commands.context):
  #  if not com.message.author.voice:
  #    await com.send("{} is not connected to a voice channel".format(
  #      com.message.author.name))
  #    return
  #  else:
  #    channel = com.message.author.voice.channel
  #    com.message.channel.send("cheers m8")
  #    await channel.connect()

  #@commands.command(name='leave',
  #                  help='Tells the bot to leave the voice channel')
  #async def leave(self, com):
  #  voice_client = com.message.guild.voice_client
  #  if voice_client.is_connected():
  #    await voice_client.disconnect()
  #  else:
  #    await com.send("the bot is not connected to a voice channel.")


async def setup(bot: commands.Bot):
  await bot.add_cog(music_cog(bot))
