import asyncio

import discord
import yt_dlp as youtube_dl
from discord.ext import commands

from main import ClientsData

# test list: https://youtube.com/playlist?list=PLEPuDqebgjKGE5p69MAYo1FIwKfx5w5cM

youtube_dl.utils.bug_reports_message = lambda: ""

ytdl_format_options = {
    "format": "bestaudio/best",
    'extractaudio': True,
    'audioformat': 'mp3',
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
        else:
            pl.append(
                {"title": data.get("title"), "url": data.get("url"), "filename": ytdl.prepare_filename(data)})
        return pl

    @classmethod
    def play_from_queue(cls, source: dict):
        return cls(discord.FFmpegPCMAudio(source["filename"], **ffmpeg_options), data=source)


class MusicCog(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    async def playListPlayer(self, ctx, gId):
        repeatBool = await ClientsData.retrieve(gId, "onLoop")
        playlist = await ClientsData.retrieve(gId, "playlist")
        if playlist is not None and (await ClientsData.retrieve(gId, "Qn") < (len(playlist) - 1)) or repeatBool:
            if not repeatBool:
                await ClientsData.set(gId, ["Qn", await ClientsData.retrieve(gId, "Qn") + 1])
            entry = playlist[await ClientsData.retrieve(gId, "Qn")]
            player = YTDLSource.play_from_queue(entry)
            await ClientsData.set(ctx.guild.id, ["CurrentlyPlaying", player.title])
            ctx.voice_client.play(
                player, after=lambda e: print(f"Player error: {e}") if e else asyncio.run_coroutine_threadsafe(
                    self.playListPlayer(ctx, gId), self.bot.loop).result()
            )
            await ctx.respond(f'Now playing: {player.title}')
        else:
            await ClientsData.set(gId, ['CurrentlyPlaying', None], ["playlist", None], ["Qn", 0])

    @commands.slash_command(name='join', description='Tells the bot to join the voice channel')
    async def join(self, ctx, channel: discord.VoiceChannel):
        if ctx.voice_client is not None:
            await ctx.respond("on the move")
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
            await ctx.respond("aven't even joined yet!")

    @commands.slash_command(name='play', description='')
    async def play(self, ctx, *, url: str):
        gId = ctx.guild.id
        if ctx.voice_client is not None and ctx.voice_client.is_connected():
            async with ctx.typing():
                await ctx.respond('On it...')
                playlist = await YTDLSource.from_url(gId, url, loop=self.bot.loop)
                await ClientsData.set(gId, ['playlist', playlist])
                player = YTDLSource.play_from_queue(playlist[await ClientsData.retrieve(gId, "Qn")])
                await ClientsData.set(ctx.guild.id, ["CurrentlyPlaying", player.title])
                ctx.voice_client.play(player, after=lambda e: print(f"Player error: {e}") if e else asyncio.run_coroutine_threadsafe(self.playListPlayer(ctx, gId),self.bot.loop).result())
        else:
            await ctx.respond('Sorry mate, unable to do so')

    @commands.slash_command(name='pause', description='Pauses the audio file currently being played by the bot')
    async def pause(self, ctx):
        if ctx.voice_client is not None and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.respond(f'Paused it for ya!')
        else:
            await ctx.respond('Sorry mate, unable to do so')

    @commands.slash_command(name='resume', description='Allows the current audio file in the queue to continue')
    async def resume(self, ctx):
        if ctx.voice_client is not None and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.respond('here ya go')
        else:
            await ctx.respond('Sorry mate, unable to do so')

    @commands.slash_command(name='onrepeat', description='Allows current audio file to repeat upon completion')
    async def OnRepeat(self, ctx, mode: bool):
        if ctx.voice_client is not None and ctx.voice_client.is_playing():
            gId = ctx.guild.id
            await ClientsData.set(gId, ["onLoop", mode])
            if mode:
                await ctx.respond(f'{await ClientsData.retrieve(gId, "CurrentlyPlaying")} will now play on loop')
            else:
                await ctx.respond('List will continue to play')
        else:
            await ctx.respond('Sorry mate, unable to do so')

    @commands.slash_command(name='previous', description='Removes the current track from the queue')
    async def previous(self, ctx):
        if ctx.voice_client is not None and ctx.voice_client.is_playing():
            gId = ctx.guild.id
            queuePlace = await ClientsData.retrieve(gId, "Qn")
            if queuePlace > 0:
                await ctx.responds('On it...')
                await ClientsData.set(gId, ["Qn", queuePlace - 2])
                ctx.voice_client.stop()
            else:
                await ctx.respond('Sorry mate, unable to do so')
        else:
            await ctx.respond('Sorry mate, unable to do so')

    @commands.slash_command(name='skip', description='Removes the current track from the queue')
    async def skip(self, ctx):
        if ctx.voice_client is not None and ctx.voice_client.is_playing():
            await ctx.respond('On it...')
            ctx.voice_client.stop()
        else:
            await ctx.respond('Sorry mate, unable to do so')

    @commands.slash_command(name='empty', description='Empties the Queue in its entirety')
    async def empty(self, ctx):
        await ctx.respond("on it")

    @commands.slash_command(name='leave', description='Tells the bot to leave the voice channel')
    async def leave(self, ctx):
        if ctx.voice_client is None:
            await ctx.respond("I ain't in a channel pal!")
        else:
            if ctx.voice_client.channel is not ctx.author.voice.channel:
                await ctx.respond('Only if you are in my channel!')
            else:
                if ctx.voice_client.is_playing():
                    ctx.voice_client.stop()
                    await discord.VoiceProtocol.disconnect(self, force=True)
                await ctx.respond("done")
                await ctx.voice_client.disconnect(force=True)

    @empty.after_invoke
    @leave.before_invoke
    async def emptyQueue(self, ctx):
        if ctx.voice_client is not None:
            await ctx.respond('Queue gone pal')
            await ClientsData.set(ctx.guild.id, ['CurrentlyPlaying', None], ['playlist', None], ['Qn', 0])
            ctx.voice_client.stop()
        else:
            await ctx.respond('Sorry mate, unable to do so')


def setup(bot):
    bot.add_cog(MusicCog(bot))
