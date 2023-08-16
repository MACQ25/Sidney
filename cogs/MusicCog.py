import asyncio
import discord
import yt_dlp as youtube_dl
from discord import VoiceProtocol
from discord.ext import commands

from main import ClientsData

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
    async def from_url(cls, cId, url, *, loop=None, stream=False):
        pl = []
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream)
        )

        # Found it, if it is a playlist "entries" will be detected :D
        if "entries" in data:

            for entry in data["entries"]:
                pl.append(
                    {"title": entry.get("title"), "url": entry.get("url"), "filename": ytdl.prepare_filename(entry)})
        return pl

    @classmethod
    def play_from_queue(cls, source: dict):
        return cls(discord.FFmpegPCMAudio(source["filename"], **ffmpeg_options), data=source)


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def playListPlayer(self, ctx, gId):
        if ClientsData.retrieve(gId, "Qn") < (len(ClientsData.retrieve(gId, "playlist")) - 1):
            ClientsData.set(gId, ["Qn", ClientsData.retrieve(gId, "Qn") + 1])
            entry = ClientsData.retrieve(gId, "playlist")[ClientsData.retrieve(gId, "Qn")]
            player = YTDLSource.play_from_queue(entry)
            ctx.voice_client.play(
                player, after=lambda e: print(f"Player error: {e}") if e else self.playListPlayer(ctx, gId))
        else:
            ClientsData.set(gId, ['CurrentlyPlaying', None], ["playlist", None], ["Qn", 0])

    @commands.slash_command(name='join', description='Tells the bot to join the voice channel')
    async def join(self, ctx, channel: discord.VoiceChannel):
        if ctx.voice_client is not None:
            ctx.respond("on the move")
            await ctx.voice_client.move_to(channel)
        else:
            await ctx.respond("goin'")
            await channel.connect()

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
        gId = ctx.guild.id
        if ctx.voice_client is not None and ctx.voice_client.is_connected():
            async with ctx.typing():
                await ctx.respond('On it...')
                playlist = await YTDLSource.from_url(gId, url, loop=self.bot.loop)
                ClientsData.set(gId, ['playlist', playlist])
                player = YTDLSource.play_from_queue(playlist[ClientsData.retrieve(gId, "Qn")])
                ctx.voice_client.play(
                    player, after=lambda e: print(f"Player error: {e}") if e else self.playListPlayer(ctx, gId))
                await ctx.send(f'Now playing: {player.title}')
                ClientsData.set(ctx.guild.id, ["CurrentlyPlaying", player.title])
        else:
            await ctx.respond('Sorry mate, unable to do so')

    @commands.slash_command(name='pause', description='Pauses the audio file currently being played by the bot')
    async def pause(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.respond(f'Paused it for ya!')
        else:
            await ctx.respond('Sorry mate, unable to do so')

    @commands.slash_command(name='resume', description='Allows the current audio file in the queue to continue')
    async def resume(self, ctx):
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.respond('here ya go')
        else:
            await ctx.respond('Sorry mate, unable to do so')

    @commands.slash_command(name='skip', description='Removes the current track from the queue')
    async def skip(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.respond('onto the next one')
            ClientsData.set(ctx.guild.id, ['CurrentlyPlaying', None])
        else:
            await ctx.respond('Sorry mate, unable to do so')

    @commands.slash_command(name='empty', description='Empties the Queue in its entirety')
    async def empty(self, ctx):
        if ctx.voice_client.is_playing():
            await ctx.respond('it is gone pal')
            ClientsData.set(ctx.guild.id, ['CurrentlyPlaying', None], ['playlist', None], ['Qn', 0])
            ctx.voice_client.stop()
        else:
            await ctx.respond('Sorry mate, unable to do so')

    @commands.slash_command(name='leave', description='Tells the bot to leave the voice channel')
    async def leave(self, ctx):
        if ctx.voice_client is None:
            await ctx.respond("I ain't in a channel ya piker!")
        else:
            if ctx.voice_client.channel is not ctx.author.voice.channel:
                await ctx.respond("You ain't in my channel ya no-hoper!")
            else:
                if ctx.voice_client.is_playing():
                    ctx.voice_client.stop()
                    await discord.VoiceProtocol.disconnect(force=True)
                await ctx.respond("done")
                await ctx.voice_client.disconnect(force=True)

    @commands.slash_command(name='sauce', description='gives sauce of song')
    async def sauce(self, ctx):
        await ctx.respond(f'it is {ClientsData.retrieve(ctx.guild.id, "CurrentlyPlaying")}')


def setup(bot):
    bot.add_cog(MusicCog(bot))
