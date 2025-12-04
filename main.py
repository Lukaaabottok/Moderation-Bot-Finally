import discord
from discord.ext import commands
import random
import os
from keep_alive import keep_alive

# --------------------------- Intents & Bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

# --------------------------- Colors & Emojis
MAIN_COLOR = 0x9B59B6
SUCCESS = "✨"
ERROR = "❌"
MOD = "🛡️"
FUN = "🎉"
GIVE = "🎁"

# --------------------------- WELCOME CHANNEL
WELCOME_CHANNEL_ID = 123456789012345678  # <-- replace with your welcome channel ID

# --------------------------- READY EVENT
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Game(".help | aesthetic ✨"))

# --------------------------- WELCOME SYSTEM
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if not channel:
        return

    embed = discord.Embed(
        title="🌸 Welcome to the Server! 🌸",
        description=(
            f"Hey {member.mention}, welcome!\n\n"
            "✨ **Enjoy your stay**\n"
            "🪄 **Make new friends**\n"
            "💜 **Be kind & have fun**"
        ),
        color=MAIN_COLOR
    )
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="🌐 Member Count", value=f"`{member.guild.member_count}` members", inline=False)
    embed.set_footer(text="Welcome • Enjoy your stay ✨")
    await channel.send(embed=embed)

# --------------------------- HELP COMMAND
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="🌸 **Aesthetic Bot Commands**",
        description="All commands grouped by category!",
        color=MAIN_COLOR
    )
    embed.add_field(
        name=f"{MOD} Moderation",
        value="`.ban` `.kick` `.mute` `.unmute` `.timeout` `.untimeout`\n`.warn` `.warns` `.clear` `.slowmode` `.lock` `.unlock`",
        inline=False
    )
    embed.add_field(
        name=f"{GIVE} Giveaways",
        value="`.gstart <time> <prize>`\n`.gend <messageID>`\n`.reroll <messageID>`",
        inline=False
    )
    embed.add_field(
        name=f"{FUN} Fun",
        value="`.say` `.avatar` `.userinfo` `.serverinfo` `.ping`",
        inline=False
    )
    await ctx.send(embed=embed)

# --------------------------- MODERATION
warns_db = {}

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.ban(reason=reason)
    embed = discord.Embed(title=f"{MOD} User Banned", description=f"**{member}** banned.\n📝 Reason: `{reason}`", color=MAIN_COLOR)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.kick(reason=reason)
    embed = discord.Embed(title=f"{MOD} User Kicked", description=f"**{member}** kicked.\n📝 Reason: `{reason}`", color=MAIN_COLOR)
    await ctx.send(embed=embed)

@bot.command()
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    if member.id not in warns_db:
        warns_db[member.id] = []
    warns_db[member.id].append(reason)
    embed = discord.Embed(title=f"{MOD} Warn Issued", description=f"**{member}** warned.\n📝 Reason: `{reason}`", color=MAIN_COLOR)
    await ctx.send(embed=embed)

@bot.command(name="warns")
async def warns(ctx, member: discord.Member):
    user_warns = warns_db.get(member.id, [])
    embed = discord.Embed(title=f"{MOD} Warning List", description="\n".join([f"• {w}" for w in user_warns]) or "No warnings.", color=MAIN_COLOR)
    await ctx.send(embed=embed)

@bot.command()
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount+1)
    embed = discord.Embed(title=f"{SUCCESS} Messages Cleared", description=f"Deleted `{amount}` messages.", color=MAIN_COLOR)
    await ctx.send(embed=embed)

@bot.command()
async def slowmode(ctx, seconds: int):
    await ctx.channel.edit(slowmode_delay=seconds)
    embed = discord.Embed(title=f"{MOD} Slowmode Set", description=f"Slowmode: `{seconds}`s", color=MAIN_COLOR)
    await ctx.send(embed=embed)

@bot.command()
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    embed = discord.Embed(title=f"{MOD} Channel Locked", description="No one can send messages.", color=MAIN_COLOR)
    await ctx.send(embed=embed)

@bot.command()
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    embed = discord.Embed(title=f"{MOD} Channel Unlocked", description="Everyone can chat now.", color=MAIN_COLOR)
    await ctx.send(embed=embed)

@bot.command()
async def timeout(ctx, member: discord.Member, seconds: int):
    await member.timeout(discord.utils.utcnow() + discord.timedelta(seconds=seconds))
    embed = discord.Embed(title=f"{MOD} Timeout Applied", description=f"{member.mention} timed out for `{seconds}`s", color=MAIN_COLOR)
    await ctx.send(embed=embed)

@bot.command()
async def untimeout(ctx, member: discord.Member):
    await member.timeout(None)
    embed = discord.Embed(title=f"{MOD} Timeout Removed", description=f"{member.mention} is no longer timed out.", color=MAIN_COLOR)
    await ctx.send(embed=embed)

# --------------------------- GIVEAWAYS
@bot.command()
async def gstart(ctx, time: str, *, prize: str):
    embed = discord.Embed(title=f"{GIVE} Giveaway Started!", description=f"🎉 Prize: **{prize}**\n⏳ Duration: `{time}`", color=MAIN_COLOR)
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎉")

@bot.command()
async def gend(ctx, message_id: int):
    msg = await ctx.channel.fetch_message(message_id)
    users = await msg.reactions[0].users().flatten()
    users.remove(bot.user)
    winner = random.choice(users)
    embed = discord.Embed(title=f"{GIVE} Giveaway Ended", description=f"🎉 Winner: {winner.mention}", color=MAIN_COLOR)
    await ctx.send(embed=embed)

@bot.command()
async def reroll(ctx, message_id: int):
    msg = await ctx.channel.fetch_message(message_id)
    users = await msg.reactions[0].users().flatten()
    users.remove(bot.user)
    winner = random.choice(users)
    embed = discord.Embed(title=f"{GIVE} Giveaway Rerolled", description=f"🎉 New Winner: {winner.mention}", color=MAIN_COLOR)
    await ctx.send(embed=embed)

# --------------------------- FUN COMMANDS
@bot.command()
async def say(ctx, *, text):
    embed = discord.Embed(description=f"💬 {text}", color=MAIN_COLOR)
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    embed = discord.Embed(title="🏓 Pong!", description=f"Latency: `{bot.latency*1000:.0f}ms`", color=MAIN_COLOR)
    await ctx.send(embed=embed)

@bot.command()
async def avatar(ctx, member: discord.Member=None):
    member = member or ctx.author
    embed = discord.Embed(title="🖼️ Avatar", color=MAIN_COLOR)
    embed.set_image(url=member.avatar.url)
    await ctx.send(embed=embed)

# --------------------------- KEEP ALIVE + RUN
keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
