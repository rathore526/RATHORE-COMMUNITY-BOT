import os
import datetime
from flask import Flask
from threading import Thread
import discord
from discord.ext import commands

# ================= KEEP ALIVE SERVER (FOR 24/7 HOSTING) =================
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# ================= BOT INITIALIZATION & CONFIGS =================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Config Placeholders (Set your values or environment variables)
MOD_LOG_CHANNEL_ID = int(os.environ.get("MOD_LOG_CHANNEL_ID", 0))
AUTO_ROLE_NAME = "Member"

PURCHASE_BANNER_URL = os.environ.get("PURCHASE_BANNER_URL", "")
PAYMENT_BANNER_URL = os.environ.get("PAYMENT_BANNER_URL", "")
SUPPORT_BANNER_URL = os.environ.get("SUPPORT_BANNER_URL", "")

UPI_ID = os.environ.get("UPI_ID", "example@upi")
UPI_NAME = os.environ.get("UPI_NAME", "Rathore X")
UPI_QR_URL = os.environ.get("UPI_QR_URL", "")

BINANCE_ID = os.environ.get("BINANCE_ID", "123456789")
BINANCE_NAME = os.environ.get("BINANCE_NAME", "Rathore X Crypto")
BINANCE_QR_URL = os.environ.get("BINANCE_QR_URL", "")

# ================= PLACEHOLDER UI VIEWS =================
class PurchaseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

class PaymentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

class SupportView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

# ================= ANTI-NUKE DUMMY FUNCTIONS =================
# Replace or connect these with your custom anti-nuke tracking logic if needed.
def check_anti_nuke(user_id: int, action_type: str) -> bool:
    return False

async def nuke_punish(guild: discord.Guild, user: discord.Member, action_type: str):
    pass

# ================= HELPER DECORATORS & FUNCTIONS =================

def anti_nuke_check(action_type):
    """
    Decorator to check anti-nuke limits before executing moderation commands.
    """
    async def predicate(ctx):
        if check_anti_nuke(ctx.author.id, action_type):
            await nuke_punish(ctx.guild, ctx.author, action_type.capitalize())
            await ctx.send(f"⚠️ **Anti-Nuke Triggered!** {ctx.author.mention} has been disciplined for exceeding action limits.", delete_after=10)
            return False
        return True
    return commands.check(predicate)

async def safe_mod_action(ctx, target: discord.Member, action_name: str, action_coro):
    """
    Safely executes moderation actions while handling permissions and error states.
    """
    if target == ctx.author:
        await ctx.send("❌ Aap khud par yeh action nahi le sakte!", delete_after=5)
        return False

    if target == ctx.guild.owner:
        await ctx.send("❌ Server Owner par yeh action nahi liya ja sakta!", delete_after=5)
        return False

    if target.top_role >= ctx.guild.me.top_role:
        await ctx.send("❌ Main is user par action nahi le sakta kyunki iska Role mere Bot Role se bada ya barabar hai!", delete_after=5)
        return False

    if target.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        await ctx.send("❌ Aap apne se barabar ya uche Role wale user par action nahi le sakte!", delete_after=5)
        return False

    try:
        await action_coro
        return True
    except discord.Forbidden:
        await ctx.send(f"❌ **Forbidden Error:** Mere paas {action_name} karne ki required permissions nahi hain.", delete_after=5)
    except Exception as e:
        await ctx.send(f"❌ Error: {e}", delete_after=5)
    return False

# ================= BOT EVENTS =================

@bot.event
async def on_ready():
    print(f"✅ Bot is online! Logged in as {bot.user}")

# ================= COMMANDS =================

@bot.command()
async def purchasepanel(ctx):
    await ctx.message.delete()
    description_text = (
        "Welcome to **RATHORE X CHEATS**, your trusted source for premium modifications, tools, and exclusive services. Create a ticket below to receive fast support, purchase assistance, or answers to your questions.\n\n"
        "📌 **RULES**\n"
        "• Create tickets only for purchases, support, or legitimate inquiries.\n"
        "• Creating tickets for fun, trolling, or wasting staff time will result in a ban.\n"
        "• All prices are listed publicly. Do not create tickets to negotiate or bargain.\n"
        "• Be respectful to staff members at all times.\n"
        "• Do not spam, ping staff repeatedly, or create multiple tickets for the same issue.\n"
        "• Payments must be completed through approved methods only.\n\n"
        "🔥 **Why Choose RATHORE X CHEATS !!**\n"
        "✓ Fast Support\n"
        "✓ Secure Transactions\n"
        "✓ Premium Quality Services\n"
        "✓ Trusted Community\n"
        "✓ Professional Assistance\n\n"
        "Click the button below to create a ticket and get started.\n\n"
        "👑 **RATHORE X CHEATS @2026 | by RATHORE !! |**"
    )
    embed = discord.Embed(description=description_text, color=discord.Color.from_rgb(88, 101, 242))
    embed.set_footer(text="Powered by Owner 1nonlyrathore8")
    if PURCHASE_BANNER_URL:
        embed.set_image(url=PURCHASE_BANNER_URL)
    await ctx.send(embed=embed, view=PurchaseView())

@bot.command()
async def paymentpanel(ctx):
    await ctx.message.delete()
    description_text = (
        "💳 **RATHORE X — PAYMENT METHODS**\n\n"
        "🔐 **SELECT YOUR PREFERRED PAYMENT METHOD**\n"
        "Choose any available payment option below to receive the complete payment details.\n\n"
        "🇮🇳 **INDIAN PAYMENT METHODS**\n"
        "• 📱 PhonePe / Paytm / Google Pay / UPI QR\n\n"
        "🟡 **CRYPTO PAYMENT METHODS**\n"
        "• 🟡 Binance Pay / USDT (TRC20/BEP20)\n\n"
        "📌 **PAYMENT INSTRUCTIONS**\n"
        "1. Select your preferred payment method.\n"
        "2. Complete payment & send clear screenshot + Transaction ID.\n"
        "3. Wait for confirmation from staff.\n\n"
        "👑 **POWERED BY RATHORE !!**"
    )
    embed = discord.Embed(description=description_text, color=discord.Color.gold())
    embed.set_footer(text="Powered by Owner 1nonlyrathore8")
    if PAYMENT_BANNER_URL:
        embed.set_image(url=PAYMENT_BANNER_URL)
    await ctx.send(embed=embed, view=PaymentView())

@bot.command()
async def supportpanel(ctx):
    await ctx.message.delete()
    description_text = (
        "🛠️ **RATHORE X CHEATS — SUPPORT TICKET**\n\n"
        "Need help? Our support team is here to assist you with technical issues, account problems, or product questions.\n\n"
        "📌 **SUPPORT RULES**\n"
        "• Open tickets only for genuine support requests.\n"
        "• Clearly explain your issue with screenshots.\n"
        "• Be respectful and patient while waiting for staff.\n\n"
        "👑 **RATHORE X CHEATS @2026 | by RATHORE !! |**"
    )
    embed = discord.Embed(description=description_text, color=discord.Color.from_rgb(57, 255, 20))
    embed.set_footer(text="Powered by Owner 1nonlyrathore8")
    if SUPPORT_BANNER_URL:
        embed.set_image(url=SUPPORT_BANNER_URL)
    await ctx.send(embed=embed, view=SupportView())

@bot.command()
async def upi(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass
    embed = discord.Embed(
        title="💳 Indian Payment Details (UPI / QR)",
        description=f"Send payment to details below and share **screenshot + Transaction ID**:\n\n"
                    f"🔹 **UPI ID:** `{UPI_ID}`\n"
                    f"🔹 **Payee Name:** {UPI_NAME}\n\n"
                    f"⚠️ *Payment complete hone ke baad screenshot zaroor bhejein!*",
        color=discord.Color.green(),
    )
    if UPI_QR_URL:
        embed.set_image(url=UPI_QR_URL)
    embed.set_footer(text="Rathore X Cheats | Secure Payment System")
    await ctx.send(embed=embed)

@bot.command()
async def binance(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass
    embed = discord.Embed(
        title="🟡 Binance / Crypto Payment Details",
        description=f"Send payment using Binance Pay ID or Crypto address:\n\n"
                    f"🔹 **Binance Pay ID / Address:** `{BINANCE_ID}`\n"
                    f"🔹 **Account Name:** {BINANCE_NAME}\n\n"
                    f"⚠️ *Double check the address before sending crypto!*",
        color=discord.Color.gold(),
    )
    if BINANCE_QR_URL and BINANCE_QR_URL != "https://your-image-url.com/binance_qr.png":
        embed.set_image(url=BINANCE_QR_URL)
    embed.set_footer(text="Rathore X Cheats | Crypto Payment System")
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass
    role = discord.utils.get(ctx.guild.roles, name=AUTO_ROLE_NAME)
    if role is None:
        await ctx.send(f"❌ Role `{AUTO_ROLE_NAME}` nahi mila!", delete_after=5)
        return
    try:
        await ctx.channel.set_permissions(role, send_messages=False)
        await ctx.send(f"🔒 **{role.name}** role ke liye yeh channel lock kar diya gaya hai!")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}", delete_after=5)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass
    role = discord.utils.get(ctx.guild.roles, name=AUTO_ROLE_NAME)
    if role is None:
        await ctx.send(f"❌ Role `{AUTO_ROLE_NAME}` nahi mila!", delete_after=5)
        return
    try:
        await ctx.channel.set_permissions(role, send_messages=True)
        await ctx.send(f"🔓 **{role.name}** role ke liye yeh channel unlock kar diya gaya hai!")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}", delete_after=5)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 {amount} messages delete kar diye gaye!", delete_after=3)

@bot.command()
@commands.has_permissions(kick_members=True)
@anti_nuke_check('kick_member')
async def kick(ctx, member: discord.Member, *, reason="Koyi reason nahi diya"):
    success = await safe_mod_action(ctx, member, "Kick", member.kick(reason=reason))
    if success:
        await ctx.send(f"🚨 {member.mention} ko kick kar diya gaya. Reason: {reason}")
        mod_channel = bot.get_channel(MOD_LOG_CHANNEL_ID)
        if mod_channel:
            embed = discord.Embed(title="👢 Member Kicked", color=discord.Color.orange())
            embed.add_field(name="User", value=f"{member.mention} ({member.name})", inline=True)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_thumbnail(url=member.display_avatar.url)
            await mod_channel.send(embed=embed)

@bot.command()
@commands.has_permissions(ban_members=True)
@anti_nuke_check('ban_member')
async def ban(ctx, member: discord.Member, *, reason="Rule break kiya"):
    success = await safe_mod_action(ctx, member, "Ban", member.ban(reason=reason))
    if success:
        await ctx.send(f"⛔ {member.mention} ko BAN kar diya gaya. Reason: {reason}")
        mod_channel = bot.get_channel(MOD_LOG_CHANNEL_ID)
        if mod_channel:
            embed = discord.Embed(title="🔨 Member Banned", color=discord.Color.dark_red())
            embed.add_field(name="User", value=f"{member.mention} ({member.name})", inline=True)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_thumbnail(url=member.display_avatar.url)
            await mod_channel.send(embed=embed)

@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, minutes: int = 10, *, reason="Rule break kiya"):
    duration = datetime.timedelta(minutes=minutes)
    success = await safe_mod_action(ctx, member, "Timeout", member.timeout(duration, reason=reason))
    if success:
        await ctx.send(f"⏳ {member.mention} ko **{minutes} minute** ke liye timeout kar diya gaya.")
        mod_channel = bot.get_channel(MOD_LOG_CHANNEL_ID)
        if mod_channel:
            embed = discord.Embed(title="⏳ Member Timed Out", color=discord.Color.gold())
            embed.add_field(name="User", value=f"{member.mention} ({member.name})", inline=True)
            embed.add_field(name="Duration", value=f"{minutes} Minutes", inline=True)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_thumbnail(url=member.display_avatar.url)
            await mod_channel.send(embed=embed)

@bot.command()
@commands.has_permissions(moderate_members=True)
async def untimeout(ctx, member: discord.Member):
    success = await safe_mod_action(ctx, member, "Untimeout", member.timeout(None))
    if success:
        await ctx.send(f"✅ {member.mention} ka timeout hata diya gaya hai.")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def price(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass

    description_text = (
        "<a:259419darkbluearrow:1550842821940879432> **RATHORE X AIMKILL**\n\n"
        "<a:259419darkbluearrow:1550842821940879432> **PANEL FEATURES**\n\n"
        "**AIM FEATURES**\n\n"
        "<a:259419darkbluearrow:1550842821940879432> AIMKILL MAX [ COVER ]\n"
        "<a:259419darkbluearrow:1550842821940879432> AIM ASSIST\n"
        "<a:259419darkbluearrow:1550842821940879432> NO HIT DELAY\n"
        "<a:259419darkbluearrow:1550842821940879432> FOV - 999X\n\n"
        "**VISUAL FEATURES**\n\n"
        "<a:259419darkbluearrow:1550842821940879432> ESP LINE\n"
        "<a:259419darkbluearrow:1550842821940879432> ESP INFO\n"
        "<a:259419darkbluearrow:1550842821940879432> ESP DISTANCE\n"
        "<a:259419darkbluearrow:1550842821940879432> ESP BOX\n"
        "<a:259419darkbluearrow:1550842821940879432> ESP CLOSEST\n"
        "<a:259419darkbluearrow:1550842821940879432> ESP GRENADE\n"
        "<a:259419darkbluearrow:1550842821940879432> ESP NAME\n"
        "<a:259419darkbluearrow:1550842821940879432> TRACKER, ETC.\n\n"
        "**MISC FEATURES**\n\n"
        "<a:259419darkbluearrow:1550842821940879432> DOWNKILL\n"
        "<a:259419darkbluearrow:1550842821940879432> EXECUTER\n"
        "<a:259419darkbluearrow:1550842821940879432> UPWARD DYNEX [ 200X ]\n"
        "<a:259419darkbluearrow:1550842821940879432> TELEPORT PLAYER\n"
        "<a:259419darkbluearrow:1550842821940879432> UPCOMING AUTO TELEPORT\n"
        "<a:259419darkbluearrow:1550842821940879432> UPCOMING JUMP REVISER\n"
        "<a:259419darkbluearrow:1550842821940879432> LOCK POSITION\n"
        "<a:259419darkbluearrow:1550842821940879432> BASE BREAKER\n"
        "<a:259419darkbluearrow:1550842821940879432> GHOST HACK\n"
        "<a:259419darkbluearrow:1550842821940879432> SHAKE KILL\n\n"
        "**GLOBAL FEATURES**\n\n"
        "<a:259419darkbluearrow:1550842821940879432> SPEED JOYSTICK\n"
        "<a:259419darkbluearrow:1550842821940879432> SPEED SCALER\n"
        "<a:259419darkbluearrow:1550842821940879432> NIGHT MODE\n"
        "<a:259419darkbluearrow:1550842821940879432> LOOK & EMOTE CHANGER\n"
        "<a:259419darkbluearrow:1550842821940879432> 11+ PREMIUM LOOK CHANGERS\n"
        "<a:259419darkbluearrow:1550842821940879432> 7+ PREMIUM EMOTE CHANGERS\n"
        "<a:259419darkbluearrow:1550842821940879432> MORE THAN 40+ FEATURES\n\n"
        "**SETTING FEATURES**\n\n"
        "<a:259419darkbluearrow:1550842821940879432> RESET GUEST\n"
        "<a:259419darkbluearrow:1550842821940879432> KEYBIND SUPPORT\n"
        "<a:259419darkbluearrow:1550842821940879432> TOPMOST SUPPORT\n"
        "<a:259419darkbluearrow:1550842821940879432> THEME SUPPORT\n"
        "<a:259419darkbluearrow:1550842821940879432> MORE THAN 40+ FEATURES\n\n"
        "**PRICES :**\n\n"
        "<a:259419darkbluearrow:1550842821940879432> **1 DAYS - 140 INR | 1.60 USD**\n"
        "<a:259419darkbluearrow:1550842821940879432> **7 DAYS - 600 INR | 7 USD**\n"
        "<a:259419darkbluearrow:1550842821940879432> **30 DAYS - 1800 INR | 20 USD**\n"
        "<a:259419darkbluearrow:1550842821940879432> **LIFETIME - 4500 INR | 40 USD**\n\n"
        "**FOR PURCHASE** <#1550562248932724756>"
    )

    embed = discord.Embed(
        description=description_text,
        color=discord.Color.from_rgb(0, 162, 255),
    )

    banner_url = "https://media.discordapp.net/attachments/1529086631536234637/1530160532974211283/standard_1.gif"
    embed.set_image(url=banner_url)

    await ctx.send(embed=embed)

@bot.command()
async def silentkill(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass

    e = "<a:259419darkbluearrow:1550842821940879432>\u3000"

    description_text = (
        f"{e}**RATHORE X SILENT KILL**\n\n"
        f"{e}**PANEL FUNCTIONS**\n\n"
        "**AIMBOT MODULE**\n\n"
        f"{e}ENABLE ALL\n"
        f"{e}SILENT AIM\n"
        f"{e}PULL 360\n"
        f"{e}SHOW BEHIND ENEMY\n"
        f"{e}FLY HACK\n"
        f"{e}TELEPORT\n"
        f"{e}GHOST\n"
        f"{e}JOYSTICK SPEED\n"
        f"{e}SPEED RUN\n\n"
        "**VISUALS MODULE**\n\n"
        f"{e}ESP LINE\n"
        f"{e}ESP BOX\n"
        f"{e}ESP NAME\n"
        f"{e}ESP HEALTH\n"
        f"{e}ESP DISTANCE\n\n"
        "**CORE USP :**\n\n"
        f"{e}REGULAR UPDATES\n"
        f"{e}FASTEST SUPPORT\n"
        f"{e}ALL SERVER SAFE\n\n"
        "**SETTINGS**\n\n"
        f"{e}RESET GUEST\n\n"
        "**PRICES**\n\n"
        f"{e}**7 DAYS - 650 INR**\n"
        f"{e}**14 DAYS - 1000 INR**\n"
        f"{e}**30 DAYS - 1850 INR**\n\n"
        "**FOR PURCHASE** <#1550562248932724756>"
    )

    embed = discord.Embed(
        description=description_text,
        color=discord.Color.from_rgb(0, 162, 255),
    )

    banner_url = "https://media.discordapp.net/attachments/1529086631536234637/1530162682630766713/standard_2.gif?ex=6aafb80c&is=6aae668c&hm=6a000d56a052d47af2d56ef4205d37be309fc40bd3ed294aea9d7abcfb9c389e&=&width=512&height=180"
    embed.set_image(url=banner_url)

    await ctx.send(embed=embed)

@bot.command()
async def emulatorbypass(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass

    e = "<a:259419darkbluearrow:1550842821940879432>\u3000"

    description_text = (
        f"{e}**RATHORE X BYPASS**\n"
        f"{e}**EMULATOR BYPASS (LIB-BASED) – NEW BR SEASON**\n\n"
        f"{e}**PLAY THE NEW BR SEASON WITHOUT RESTRICTIONS**\n\n"
        "**FEATURES**\n\n"
        f"{e}NO UID RESTRICTION\n"
        f"{e}PLAY ON UNLIMITED IDS\n"
        f"{e}SAFE FOR MAIN ACCOUNT\n"
        f"{e}NO LIMIT ON KILLS\n\n"
        "**PRICING**\n\n"
        f"{e}**1 DAY – ₹120**\n"
        f"{e}**7 DAYS – ₹500**\n"
        f"{e}**15 DAYS – ₹800**\n"
        f"{e}**1 MONTH – ₹1500**\n"
        f"{e}**PERMANENT – ₹4500**\n\n"
        "**FOR PURCHASE** <#1550562248932724756>"
    )

    embed = discord.Embed(
        description=description_text,
        color=discord.Color.from_rgb(0, 162, 255),
    )

    banner_url = "https://media.discordapp.net/attachments/1490095245302431868/1518999070457200752/standard.gif?ex=6aaf50e0&is=6aadff60&hm=8181c16843246bf0ffb50c20d1287345ecd9640de6680179147a858c8d95ce8a&="
    embed.set_image(url=banner_url)

    await ctx.send(embed=embed)

@bot.command()
async def paidpush(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass

    e = "<a:259419darkbluearrow:1550842821940879432>\u3000"

    description_text = (
        f"{e}**RATHORE X PAID PUSH**\n\n"
        f"{e}**PAID PUSH PRICING**\n\n"
        f"{e}**20 STAR = 80 INR**\n"
        f"{e}**40 STAR = 160 INR**\n"
        f"{e}**60 STAR = 240 INR**\n"
        f"{e}**80 STAR = 320 INR**\n"
        f"{e}**100 STAR = 400 INR**\n"
        f"{e}**200 STAR = 800 INR**\n"
        f"{e}**300 STAR = 1200 INR**\n"
        f"{e}**400 STAR = 1600 INR**\n"
        f"{e}**500 STAR = 2000 INR**\n"
        f"{e}**999 STAR = 2999 INR**\n\n"
        "**FOR PURCHASE** <#1550562248932724756>"
    )

    embed = discord.Embed(
        description=description_text,
        color=discord.Color.from_rgb(0, 162, 255),
    )

    banner_url = "https://media.discordapp.net/attachments/1490095245302431868/1519005559347478818/standard_2.gif?ex=6aaf56eb&is=6aae056b&hm=241c3c051ae74c731f460040df41c73d236d800cd077cce8387690ee7d9aa01c&"
    embed.set_image(url=banner_url)

    await ctx.send(embed=embed)

@bot.command()
async def level8ids(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass

    e = "<a:259419darkbluearrow:1550842821940879432>\u3000"

    description_text = (
        f"{e}**LV 8 IDS**\n\n"
        f"{e}**STOCK = UNLIMITED**\n\n"
        f"{e}**PRICE: 5 ID IN JUST 100 INR**\n\n"
        "**FOR PURCHASE** <#1550562248932724756>"
    )

    embed = discord.Embed(
        description=description_text,
        color=discord.Color.from_rgb(0, 162, 255),
    )

    banner_url = "https://media.discordapp.net/attachments/1490095245302431868/1519001574742036761/standard_1.gif?ex=6aaf5335&is=6aae01b5&hm=93a8da68d2d2238bd90cf9bc0c98af2dd89eb8f02c177b8bd8f094d9b4132b98&="
    embed.set_image(url=banner_url)

    await ctx.send(embed=embed)

@bot.command()
async def rules(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass

    e = "<a:259419darkbluearrow:1550842821940879432>\u3000"

    description_text = (
        f"{e}**RATHORE X RULES**\n\n"
        f"{e}**WELCOME TO RATHORE SERVER !!**\n\n"
        "**BE RESPECTFUL :**\n"
        f"{e}TREAT EVERYONE WITH RESPECT. NO TOXIC BEHAVIOR, HATE SPEECH, PERSONAL ATTACKS, IMPERSONATION, FALSE ACCUSATIONS, OR ANY DISRESPECTFUL CONDUCT WILL BE TOLERATED.\n\n"
        "**KEEP CHANNELS CLEAN :**\n"
        f"{e}NO SPAMMING, COPYING & PASTING REPEATEDLY, BEGGING, ADVERTISING OTHER SERVERS, OR POSTING NSFW/DISTURBING CONTENT. DISCUSSIONS ABOUT CHEATS OR ANY ILLEGAL ACTIVITY ARE STRICTLY PROHIBITED.\n\n"
        "**NO PROMOTION :**\n"
        f"{e}PROMOTION OF OTHER SERVERS, PRODUCTS, OR SERVICES WITHOUT PERMISSION IS STRICTLY PROHIBITED.\n\n"
        "**USE APPROPRIATE NAMES & PROFILES :**\n"
        f"{e}CHOOSE A CLEAN, NON-OFFENSIVE USERNAME, AVATAR, AND PROFILE. INAPPROPRIATE OR OFFENSIVE CONTENT WILL BE REMOVED IMMEDIATELY.\n\n"
        "**NO FILTER OR PUNISHMENT EVASION :**\n"
        f"{e}DO NOT TRY TO BYPASS FILTERS OR PUNISHMENTS. DOING SO WILL LEAD TO FURTHER DISCIPLINARY ACTION.\n\n"
        "**SUPPORT POLICY :**\n"
        f"{e}THERE IS NO SUPPORT FOR FREE IMGUI VERSIONS. IF YOU HAVE PURCHASED A PRODUCT, YOU GET 3 DAYS OF FREE SUPPORT ONLY. DMING STAFF DIRECTLY WILL LEAD TO TIMEOUTS OR PERMANENT BANS.\n\n"
        "**STAY INFORMED :**\n"
        f"{e}PLEASE READ ALL CHANNELS CAREFULLY, INCLUDING OUR TERMS OF SERVICE, REFUND POLICY, AND PRIVACY POLICY, AVAILABLE ON THE WEBSITE AND SERVER.\n\n"
        "**REFUND POLICY :**\n"
        f"{e}WE STRIVE TO PROVIDE QUALITY SERVICES AND PRODUCTS. REFUNDS ARE CONSIDERED ONLY UNDER GENUINE ISSUES AND WITHIN A LIMITED TIMEFRAME. PLEASE CONTACT SUPPORT PROMPTLY WITH VALID REASONS. ALL REFUND REQUESTS ARE SUBJECT TO REVIEW AND APPROVAL.\n\n"
        f"{e}**BY JOINING RATHORE SERVER , YOU AGREE TO FOLLOW THESE RULES. THANK YOU FOR HELPING US BUILD A RESPECTFUL AND TRUSTWORTHY COMMUNITY**\n\n"
    )

    embed = discord.Embed(
        description=description_text,
        color=discord.Color.from_rgb(0, 162, 255),
    )

    banner_url = "https://media.discordapp.net/attachments/1529086631536234637/1548911076505030656/SERVER_RULES.gif?ex=6aaf5eda&is=6aae0d5a&hm=21191945043f4c5293e08011c7f95b141ab0078bacf8a44730b450f859cb6114&"
    embed.set_image(url=banner_url)

    await ctx.send(embed=embed)

# ================= RUN SERVER & BOT =================
if __name__ == "__main__":
    keep_alive()
    token = os.environ.get("DISCORD_TOKEN") or os.getenv("TOKEN") or os.environ.get("DISCORD_BOT_TOKEN")
    if token:
        bot.run(token)
    else:
        print("❌ Token nahi mila! Kripya environment variables check karein.")
