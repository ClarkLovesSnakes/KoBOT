from __future__ import annotations
import discord
from discord.ext import commands
import asyncio
from typing import TextIO
import yt_dlp
import logging
import random
import tomllib
import re


class QuirkNotFoundError(Exception):
    pass


class YDLSource(discord.PCMVolumeTransformer):
    ydl_format_options = {
        'format': 'bestaudio/best',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
    }
    ffmpeg_options = {
            "options": "-vn",
            }


    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(cls.ydl_format_options) as ydl:

            data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=(not stream)))

            if "entries" in data:
                data = data["entries"][0]

            filename = data["url"] if stream else ydl.prepare_filename(data)
            return cls(discord.FFmpegPCMAudio(filename, **cls.ffmpeg_options), data=data)


class KoBot(commands.Cog):
    def __init__(self, bot, quirks):
        self.bot = bot
        self.quirks = quirks

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def join(self, ctx, *, channel: discord.VoiceChannel | None = None):
        """Joins a voice channel"""

        if channel is None:
            if ctx.author.voice is None:
                return await ctx.reply("You are not in a voice channel")
            channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def play(self, ctx, *, query):
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print(f"Player error: {e}") if e else None)

        await ctx.send(f"Now playing: {query}")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def yt(self, ctx, *, url):
        async with ctx.typing():
            player = await YDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print(f"Player error: {e}") if e else None)

            await ctx.send(f"Now playing: {player.title}")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def stream(self, ctx, *, url):
        async with ctx.typing():
            player = await YDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f"Player error: {e}") if e else None)

        await ctx.send(f"Now playing: {player.title}")


    @commands.command()
    async def pause(self, ctx):
        await ctx.voice_client.pause()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def resume(self, ctx):
        await ctx.voice_client.resume()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def leave(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()


    @play.before_invoke
    @yt.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


    @commands.command(aliases=["rr", "regr", "rroll", "regroll", "regularroll", "reg_roll"])
    async def regular_roll(self, ctx, *args):

        times = 1
        sides = 20
        mods = []

        if args:
            args = "".join(args)
            mods_re = re.compile("[+-]\d+")
            mods = mods_re.findall(args)
            for m in mods:
                args = args[:args.find(m)] + args[args.find(m) + len(m):]

            mods = [int(m) for m in mods]

            ndn_re = re.compile("\d*[dD]?[+-]?\d+")
            ndns = ndn_re.search(args)

            if ndns:
                match = ndns.group()
                if "d" in match or "D" in match:
                    if "d" in match:
                        times, sides = match.split("d")
                    elif "D" in match:
                        times, sides = match.split("D")
                    if not times:
                        times = 1

                else:
                    sides = match
                    times = 1

            else:
                sides = 20

            if isinstance(sides, str):
                sides = int(sides)

            if isinstance(times, str):
                times = int(times)

        rolls = [random.randint(1, sides) for _ in range(times)]

        result = ""
        if times > 1:
            result += " + ".join(str(r) for r in rolls)

        else:
            result += str(rolls[0])

        if len(mods) > 0:
            mods_str = ""
            start, *mods = mods
            for m in mods:
                if m >= 0:
                    mods_str += " + "
                else:
                    mods_str += " - "
                mods_str += str(abs(m))
            if start >= 0:
                result += f" + {abs(start)}{mods_str}"
            else:
                result += f" - {abs(start)}{mods_str}"

        if times > 1 or len(mods) > 0:
            final_sum = sum(rolls) + sum(mods)
            result += f": **{final_sum}**"

        else:
            result = f"**{result}**"

        await ctx.reply(result)


    @commands.command(aliases=["r", "kr", "kanvesr", "kroll", "knavesroll", "knavroll", "k_roll", "roll"])
    async def knaves_roll(self, ctx, *args):

        times = 2
        sides = 6
        fort = []
        mis = []
        mods = []

        if args:
            args = "".join(args)
            mods_re = re.compile("[+-]\d+")
            mods = mods_re.findall(args)
            for m in mods:
                args = args[:args.find(m)] + args[args.find(m) + len(m):]

            mods = [int(m) for m in mods]

            fort_re = re.compile("\d+f[a-zA-Z]*")
            fort = fort_re.findall(args)
            for f in fort:
                args = args[:args.find(f)] + args[args.find(f) + len(f):]

            fort_num_re = re.compile("\d+")
            fort = [int(fort_num_re.match(f).group()) for f in fort]

            mis_re = re.compile("\d+m[a-zA-Z]*")
            mis = mis_re.findall(args)
            for m in mis:
                args = args[:args.find(m)] + args[args.find(m) + len(m):]

            mis_num_re = re.compile("\d+")
            mis = [int(mis_num_re.match(m).group()) for m in mis]

            times += sum(fort) + sum(mis)

        rolls = [random.randint(1, sides) for _ in range(times)]

        result = ", ".join(str(r) for r in rolls)

        quirk = all(rolls[0] == r for r in rolls)

        rolls = sorted(rolls)
        for _ in range(sum(fort)):
            del rolls[0]

        rolls = list(reversed(rolls))
        for _ in range(sum(mis)):
            del rolls[0]

        assert len(rolls) == 2
        roll_sums = " + ".join(str(r) for r in rolls)
        result += f"\n{roll_sums}"

        snake_eyes = False
        bookshelves = False
        if rolls[0] == 1 and rolls[1] == 1:
            mods = [-1 * abs(m) for m in mods]
            snake_eyes = True

        elif rolls[0] == sides and rolls[1] == sides:
            mods = [abs(m) for m in mods]
            bookshelves = True

        if len(mods) > 0:
            mods_str = ""
            start, *_mods = mods
            for m in _mods:
                if m >= 0:
                    mods_str += " + "
                else:
                    mods_str += " - "
                mods_str += str(abs(m))
            if start >= 0:
                result += f" + {abs(start)}{mods_str}"
            else:
                result += f" - {abs(start)}{mods_str}"

        if times > 1 or len(mods) > 0:
            final_sum = sum(rolls) + sum(mods)
            result += f" = **{final_sum}**"

        else:
            result = f"**{result}**"

        if snake_eyes:
            result += "\n**Snake Eyes!**"

        if bookshelves:
            result += "\n**Bookshelves!**"

        if quirk and times == 2:
            quirk_roll = random.randint(1, sides)
            result += f"\nQuirk Roll: {quirk_roll}"
            quirk = quirk_roll == rolls[0]

        if quirk:
            if times > 3:
                adv_number, adv_name, adv_text = self._quirk("advantage")
                result += f"\n**{str(adv_number).strip()}. {adv_name.strip()}:\n**{adv_text.strip()}"
                for _ in range(2):
                    number, name, text = self._quirk()
                    result += f"\n**{str(number).strip()}. {name.strip()}:** {text.strip()}"

            else:
                number, name, text = self._quirk()
                result += f"\n**{str(number).strip()}. {name.strip()}:** {text.strip()}"

        await ctx.reply(result)


    @commands.command(aliases=["f", "froll", "fort", "fortune", "fortuneroll"])
    async def fortune_roll(self, ctx, *args):
        if args:
            args = "".join(args)
            mods_re = re.compile("[+-]\d+")
            mods = mods_re.findall(args)
            for m in mods:
                args = args[:args.find(m)] + args[args.find(m) + len(m):]

            fort_re = re.compile("\d+")
            num_fort = fort_re.match(args).group()

            final_input = f"{num_fort}f"
            for m in mods:
                if m >= 0:
                    final_input += f"+{abs(m)}"
                else:
                    final_input += f"-{abs(m)}"

            return await self.knaves_roll(ctx, final_input)

        else:
            return await self.knaves_roll(ctx, "1f")


    @commands.command(aliases=["m", "mroll", "mis", "misfortune", "misfortuneroll"])
    async def misfortune_roll(self, ctx, *args):
        if args:
            args = "".join(args)
            mods_re = re.compile("[+-]\d+")
            mods = mods_re.findall(args)
            for m in mods:
                args = args[:args.find(m)] + args[args.find(m) + len(m):]

            fort_re = re.compile("\d+")
            num_fort = fort_re.match(args).group()

            final_input = f"{num_fort}m"
            for m in mods:
                if m >= 0:
                    final_input += f"+{abs(m)}"
                else:
                    final_input += f"-{abs(m)}"

            return await self.knaves_roll(ctx, final_input)

        else:
            return await self.knaves_roll(ctx, "1m")


    @commands.command(aliases=["q"])
    async def quirk(self, ctx, *args):

        try:
            number, name, text = self._quirk(args)
        except QuirkNotFoundError as e:
            return await ctx.reply(e)

        else:
            if number.isdigit():
                return await ctx.reply(f"**{str(number).strip()}. {name.strip()}:** {text.strip()}")
            else:
                return await ctx.reply(f"**{str(number).strip()}. {name.strip()}:**\n{text.strip()}")


    def _quirk(self, args=None):
        initial_input = None
        if not args:
            quirk = str(random.randint(1, 20))
        else:
            initial_input = "".join(args)
            quirk = "".join(initial_input.split()).lower()

        if quirk not in self.quirks:
            for n, d in self.quirks.items():
                if quirk == d["name"].lower():
                    quirk = n

        if quirk not in self.quirks:
            raise QuirkNotFoundError(f"{initial_input} is not a valid quirk!")

        q = self.quirks[quirk]
        number = str(q["number"])
        name = q["name"]
        text = q["text"]

        return number, name, text


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot: commands.Bot
bot = commands.Bot(
        intents=intents,
        command_prefix=commands.when_mentioned_or("!"),
        strip_after_prefix=True,
        case_insensitive=True
        )


@bot.event
async def on_ready():
    await bot.change_presence(activity = discord.Game(name = "Knaves of the Oblong Stool"))
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("-------------------------------------------")


async def main():

    discord.utils.setup_logging(level=logging.INFO, root=False)

    fp: TextIO
    with open("quirks.toml", "rb") as fp:
        quirks = tomllib.load(fp)

    with open("Token.txt", "r", encoding="utf-8") as fp:
        token = fp.read()

    async with bot:
        await bot.add_cog(KoBot(bot, quirks))
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
