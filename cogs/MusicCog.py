import discord
import youtube_dl
from discord.ext import commands

youtube_dl.utils.bug_reports_message = lambda: ""

ytdl_format_options = {
    "format": "bestaudio/best",
    "ext": "mp3",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": (
        "0.0.0.0"
    ),  # Bind to ipv4 since ipv6 addresses cause issues at certain times
}

ffmpeg_options = {"options": "-vn"}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name='join', description='Tells the bot to join the voice channel')
    async def join(self, ctx):
        if not ctx.author.voice:
            await ctx.respond("{} is not connected to a voice channel".format(ctx.author.name))
        else:
            if ctx.voice_client is None:
                await ctx.respond("cheers m8")
                channel = ctx.author.voice.channel
                await channel.connect()
            else:
                await ctx.respond("Already in a channel m8")

    @discord.slash_command(name='leave', description='Tells the bot to leave the voice channel')
    async def leave(self, com):
        if com.voice_client is None:
            await com.respond("I ain't in a channel ya piker!")
        else:
            if com.voice_client.channel is not com.author.voice.channel:
                await com.respond("You ain't in my channel ya no-hoper!")
            else:
                await com.voice_client.disconnect(force=True)
                await com.respond("done")


def setup(bot):
    bot.add_cog(MusicCog(bot))
