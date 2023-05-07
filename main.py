import asyncio
import yt_dlp
import discord
from discord.ext import commands

queue = []
token = ''

# Suppress noise about console usage from errors
yt_dlp.utils.bug_reports_message = lambda: ""

ytdl_format_options = {
    "format": "bestaudio/best",
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
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)


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
            None, lambda: ytdl.extract_info(url, download=not stream))

        if "entries" in data:
            # Takes the first item from a playlist
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot_: commands.Bot):
        self.bot = bot_

    @commands.command()
    async def join(self, ctx: commands.Context, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()

    @commands.command()
    async def play(self, ctx: commands.Context, *, url: str):
        """Plays from a url (almost anything youtube_dl supports)"""
        global queue                        
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=False)
            ctx.voice_client.play(player, after=lambda e: self.play_next(ctx))                
        await ctx.send(f"Now playing: {player.title}")
        


    def play_next(self, ctx: commands.Context):
        global queue
        if len(queue) > 0:
            player = queue.pop(0)
            ctx.voice_client.play(player, after=lambda e: self.play_next(ctx))
    
    @commands.command()
    async def clear(self, ctx: commands.Context):
        '''clear queue'''        
        global queue
        queue = []
        await ctx.send(f"**Queue cleared!**")

    @commands.command()
    async def q(self,ctx: commands.Context, *, url: str):
        '''add song to queue'''
        global queue
        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=False)               
        print('DEBUG!!!!! q')
        queue.append(player)
        print('DEBUG global queue:   '+str(queue)) 
        await ctx.send(f':mag_right: **Searching for:** ``' + url + '``\n**Added to queue:** ``{}'.format(player.title) + "``")
        print('DEBUG:   '+str(len(queue)))
    
    @commands.command()
    async def skip(self, ctx: commands.Context):
        """Skips the current song"""
        global queue
        if len(queue) > 0:
            ctx.voice_client.stop()            
            await ctx.send(f"**Skipped to the next song in the queue.**")
        else:
            await ctx.send(f"**Last song in queue... Stopping playback!**")

    @commands.command()
    async def vol(self, ctx: commands.Context, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command()
    async def stop(self, ctx: commands.Context):
        """Stops and disconnects the bot from voice"""
        global queue
        queue = []
        await ctx.voice_client.disconnect(force=True)

    @play.before_invoke
    @skip.before_invoke
    
    async def ensure_voice(self, ctx: commands.Context):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description="Relatively simple music bot example",
    intents=intents,)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

bot.add_cog(Music(bot))
bot.run(token)
