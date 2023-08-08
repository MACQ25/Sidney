import asyncio
import discord
import yt_dlp as youtube_dl
from discord.ext import commands

youtube_dl.utils.bug_reports_message = lambda: ""

ytdl_format_options = {
    "format": "wav/bestaudio/best",
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


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source: discord.AudioSource, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream)
        )
        if "entries" in data:
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='join', description='Tells the bot to join the voice channel')
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

    @commands.slash_command(name='leave', description='Tells the bot to leave the voice channel')
    async def leave(self, com):
        if com.voice_client is None:
            await com.respond("I ain't in a channel ya piker!")
        else:
            if com.voice_client.channel is not com.author.voice.channel:
                await com.respond("You ain't in my channel ya no-hoper!")
            else:
                if com.voice_client.is_playing():
                    com.voice_client.stop()
                await com.respond("done")
                await com.voice_client.disconnect(force=True)

    @commands.slash_command(name='playlocal',
                            description='Plays from local computer (functionality on systems without ffmpeg is uncertain [likely not])')
    async def playlocal(self, ctx, *, query: str):
        if ctx.voice_client is not None:
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
            ctx.voice_client.play(source, after=lambda e: print(f"Player error: {e}") if e else None)
            await ctx.respond(f'Now playing {query}')
        else:
            await ctx.respond("aven't even joined ya booksmarts!")

    @commands.slash_command(name='play', description='')
    async def play(self, ctx, *, url: str):
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            await ctx.respond(f'Now playing: {player.title}')
            ctx.voice_client.play(
                player, after=lambda e: print(f"Player error: {e}") if e else None
            )


def setup(bot):
    bot.add_cog(MusicCog(bot))
