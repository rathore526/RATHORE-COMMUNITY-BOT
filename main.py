import datetime
import os
import discord
from discord.ext import commands

# Keep Alive server import (agar aap replit/render/glitch wagerah par hosting kar rahe hain)
try:
    from keep_alive import keep_alive
except ImportError:

    def keep_alive():
        pass


# Bot Setup & Constants (Apne hisab se IDs check kar lein)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Placeholders for Variables (Yahan apni variables define karein agar pehle se nahi hain)
AUDIT_LOG_CHANNEL_ID = 123456789012345678
MOD_LOG_CHANNEL_ID = 123456789012345678
PURCHASE_TICKET_CHANNEL_ID = 123456789012345678
SUPPORT_TICKET_CHANNEL_ID = 123456789012345678
PAYMENT_TICKET_CHANNEL_ID = 123456789012345678

PURCHASE_BANNER_URL = ""
SUPPORT_BANNER_URL = ""
PAYMENT_BANNER_URL = ""

UPI_ID = "example@upi"
UPI_NAME = "Your Name"
UPI_QR_URL = ""

BINANCE_ID = "12345678"
BINANCE_NAME = "Your Binance Name"
BINANCE_QR_URL = ""

AUTO_ROLE_NAME = "Member"


# Mock Classes for Views (Inhe apne original View classes se replace karein)
class PurchaseView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)


class SupportView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)


class PaymentView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)


# --- AUDIT LOG LISTENERS ---
@bot.event
async def on_message_delete(message):
    if message.author and message.author.bot:
        return

    log_channel = bot.get_channel(AUDIT_LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(
            title="🗑️ Message Deleted",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow(),
        )
        author_str = (
            f"{message.author.mention} (`{message.author.id}`)"
            if message.author
            else "Unknown User"
        )
        embed.add_field(name="Author", value=author_str, inline=True)
        embed.add_field(
            name="Channel",
            value=message.channel.mention if message.channel else "Unknown",
            inline=True,
        )
        embed.add_field(
            name="Content",
            value=(
                message.content
                if message.content
                else "*[Image/Attachment/Uncached Message]*"
            ),
            inline=False,
        )
        embed.set_footer(text=f"Message ID: {message.id}")
        await log_channel.send(embed=embed)


@bot.event
async def on_message_edit(before, after):
    if before.author and before.author.bot:
        return
    if before.content == after.content:
        return

    log_channel = bot.get_channel(AUDIT_LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(
            title="✏️ Message Edited",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow(),
        )
        author_str = (
            f"{before.author.mention} (`{before.author.id}`)"
            if before.author
            else "Unknown User"
        )
        embed.add_field(name="Author", value=author_str, inline=True)
        embed.add_field(
            name="Channel",
            value=before.channel.mention if before.channel else "Unknown",
            inline=True,
        )
        embed.add_field(
            name="Before",
            value=before.content if before.content else "*Empty*",
            inline=False,
        )
        embed.add_field(
            name="After",
            value=after.content if after.content else "*Empty*",
            inline=False,
        )
        embed.set_footer(text=f"Message ID: {before.id}")
        await log_channel.send(embed=embed)


# ================= COMMANDS =================


@bot.command()
@commands.has_permissions(administrator=True)
async def setup_tickets(ctx):
    p_chan = bot.get_channel(PURCHASE_TICKET_CHANNEL_ID)
    if p_chan:
        embed_p = discord.Embed(
            title="🛒 Open Purchase Ticket",
            description="Select an option below to buy cheats or products.",
            color=discord.Color.blue(),
        )
        if PURCHASE_BANNER_URL:
            embed_p.set_image(url=PURCHASE_BANNER_URL)
        await p_chan.send(embed=embed_p, view=PurchaseView())

    s_chan = bot.get_channel(SUPPORT_TICKET_CHANNEL_ID)
    if s_chan:
        embed_s = discord.Embed(
            title="🛠️ Open Support Ticket",
            description="Select an option below to get assistance from staff.",
            color=discord.Color.green(),
        )
        if SUPPORT_BANNER_URL:
            embed_s.set_image(url=SUPPORT_BANNER_URL)
        await s_chan.send(embed=embed_s, view=SupportView())

    pay_chan = bot.get_channel(PAYMENT_TICKET_CHANNEL_ID)
    if pay_chan:
        embed_pay = discord.Embed(
            title="💳 Payment Methods",
            description="Select your preferred payment method below.",
            color=discord.Color.gold(),
        )
        if PAYMENT_BANNER_URL:
            embed_pay.set_image(url=PAYMENT_BANNER_URL)
        await pay_chan.send(embed=embed_pay, view=PaymentView())

    await ctx.send(
        "✅ Purchase, Support aur Payment Teeno Ticket Panels Setup Ho Gaye"
        " Hain!"
    )


@bot.command()
@commands.has_permissions(administrator=True)
async def purchasepanel(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        title="🛒 RATHORE X CHEATS - PURCHASE",
        description=(
            "Select an option below to buy cheats or inquire about product"
            " pricing."
        ),
        color=discord.Color.from_rgb(88, 101, 242),
    )
    if PURCHASE_BANNER_URL:
        embed.set_image(url=PURCHASE_BANNER_URL)
    await ctx.send(embed=embed, view=PurchaseView())


@bot.command()
@commands.has_permissions(administrator=True)
async def paymentpanel(ctx):
    await ctx.message.delete()
    description_text = (
        "💳 **RATHORE X — PAYMENT METHODS**\n\n"
        "🔐 **SELECT YOUR PREFERRED PAYMENT METHOD**\n"
        "Choose any available payment option below to receive the complete"
        " payment details.\n\n"
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
    embed = discord.Embed(
        description=description_text, color=discord.Color.gold()
    )
    embed.set_footer(text="Powered by Owner 1nonlyrathore8")
    if PAYMENT_BANNER_URL:
        embed.set_image(url=PAYMENT_BANNER_URL)
    await ctx.send(embed=embed, view=PaymentView())


@bot.command()
@commands.has_permissions(administrator=True)
async def supportpanel(ctx):
    await ctx.message.delete()
    description_text = (
        "🛠️ **RATHORE X CHEATS — SUPPORT TICKET**\n\n"
        "Need help? Our support team is here to assist you with technical"
        " issues, account problems, or product questions.\n\n"
        "📌 **SUPPORT RULES**\n"
        "• Open tickets only for genuine support requests.\n"
        "• Clearly explain your issue with screenshots.\n"
        "• Be respectful and patient while waiting for staff.\n\n"
        "👑 **RATHORE X CHEATS @2026 | by RATHORE !! |**"
    )
    embed = discord.Embed(
        description=description_text, color=discord.Color.from_rgb(57, 255, 20)
    )
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
        description=(
            "Send payment to details below and share **screenshot +"
            f" Transaction ID**:\n\n🔹 **UPI ID:** `{UPI_ID}`\n🔹 **Payee"
            f" Name:** {UPI_NAME}\n\n⚠️ *Payment complete hone ke baad"
            " screenshot zaroor bhejein!*"
        ),
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
        description=(
            "Send payment using Binance Pay ID or Crypto address:\n\n🔹"
            f" **Binance Pay ID / Address:** `{BINANCE_ID}`\n🔹 **Account Name:**"
            f" {BINANCE_NAME}\n\n⚠️ *Double check the address before sending"
            " crypto!*"
        ),
        color=discord.Color.gold(),
    )
    if (
        BINANCE_QR_URL
        and BINANCE_QR_URL != "https://your-image-url.com/binance_qr.png"
    ):
        embed.set_image(url=BINANCE_QR_URL)
    embed.set_footer(text="Rathore X Cheats | Crypto Payment System")
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.message.delete()
    role = discord.utils.get(ctx.guild.roles, name=AUTO_ROLE_NAME)
    if role is None:
        await ctx.send(f"❌ Role `{AUTO_ROLE_NAME}` nahi mila!", delete_after=5)
        return
    try:
        await ctx.channel.set_permissions(role, send_messages=False)
        await ctx.send(
            f"🔒 **{role.name}** role ke liye yeh channel lock kar diya gaya hai!"
        )
    except Exception as e:
        await ctx.send(f"❌ Error: {e}", delete_after=5)


@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.message.delete()
    role = discord.utils.get(ctx.guild.roles, name=AUTO_ROLE_NAME)
    if role is None:
        await ctx.send(f"❌ Role `{AUTO_ROLE_NAME}` nahi mila!", delete_after=5)
        return
    try:
        await ctx.channel.set_permissions(role, send_messages=True)
        await ctx.send(
            f"🔓 **{role.name}** role ke liye yeh channel unlock kar diya gaya"
            " hai!"
        )
    except Exception as e:
        await ctx.send(f"❌ Error: {e}", delete_after=5)


@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 {amount} messages delete kar diye gaye!", delete_after=3)


@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Koyi reason nahi diya"):
    await member.kick(reason=reason)
    await ctx.send(
        f"🚨 {member.mention} ko kick kar diya gaya. Reason: {reason}"
    )

    mod_channel = bot.get_channel(MOD_LOG_CHANNEL_ID)
    if mod_channel:
        embed = discord.Embed(
            title="👢 Member Kicked", color=discord.Color.orange()
        )
        embed.add_field(
            name="User",
            value=f"{member.mention} ({member.name})",
            inline=True,
        )
        embed.add_field(
            name="Moderator", value=ctx.author.mention, inline=True
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        await mod_channel.send(embed=embed)


@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Rule break kiya"):
    await member.ban(reason=reason)
    await ctx.send(f"⛔ {member.mention} ko BAN kar diya gaya. Reason: {reason}")

    mod_channel = bot.get_channel(MOD_LOG_CHANNEL_ID)
    if mod_channel:
        embed = discord.Embed(
            title="🔨 Member Banned", color=discord.Color.dark_red()
        )
        embed.add_field(
            name="User",
            value=f"{member.mention} ({member.name})",
            inline=True,
        )
        embed.add_field(
            name="Moderator", value=ctx.author.mention, inline=True
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        await mod_channel.send(embed=embed)


@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(
    ctx,
    member: discord.Member,
    minutes: int = 10,
    *,
    reason="Rule break kiya",
):
    if member == ctx.author:
        await ctx.send("❌ Aap khud ko timeout nahi de sakte!")
        return

    if member.top_role >= ctx.guild.me.top_role:
        await ctx.send(
            "❌ Main is user ko timeout nahi de sakta kyunki iska Role mere Bot"
            " Role se bada ya barabar hai!"
        )
        return

    duration = datetime.timedelta(minutes=minutes)
    try:
        await member.timeout(duration, reason=reason)
        await ctx.send(
            f"⏳ {member.mention} ko **{minutes} minute** ke liye timeout kar"
            " diya gaya."
        )

        mod_channel = bot.get_channel(MOD_LOG_CHANNEL_ID)
        if mod_channel:
            embed = discord.Embed(
                title="⏳ Member Timed Out", color=discord.Color.gold()
            )
            embed.add_field(
                name="User",
                value=f"{member.mention} ({member.name})",
                inline=True,
            )
            embed.add_field(
                name="Duration", value=f"{minutes} Minutes", inline=True
            )
            embed.add_field(
                name="Moderator", value=ctx.author.mention, inline=True
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_thumbnail(url=member.display_avatar.url)
            await mod_channel.send(embed=embed)

    except discord.Forbidden:
        await ctx.send(
            "❌ **Forbidden Error:** Mere paas `Moderate Members` permission"
            " nahi hai ya yeh user Admin hai."
        )
    except Exception as e:
        await ctx.send(f"❌ Error: {e}", delete_after=5)


@bot.command()
@commands.has_permissions(moderate_members=True)
async def untimeout(ctx, member: discord.Member):
    try:
        await member.timeout(None)
        await ctx.send(f"✅ {member.mention} ka timeout hata diya gaya hai.")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}", delete_after=5)


@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")


@bot.command()
@commands.has_permissions(administrator=True)
async def price(ctx):
    await ctx.message.delete()

    description_text = (
        "**RATHORE X AIMKILL**\n"
        "**PANEL FEATURES**\n\n"
        "**AIM FEATURES**\n"
        "• AIMKILL MAX [ COVER ]\n"
        "• AIM ASSIST\n"
        "• NO HIT DELAY\n"
        "• FOV - 999X\n\n"
        "**VISUAL FEATURES**\n"
        "• ESP LINE\n"
        "• ESP INFO\n"
        "• ESP DISTANCE\n"
        "• ESP BOX\n"
        "• ESP CLOSEST\n"
        "• ESP GRENADE\n"
        "• ESP NAME\n"
        "• TRACKER, ETC.\n\n"
        "**MISC FEATURES**\n"
        "• DOWNKILL\n"
        "• EXECUTER\n"
        "• UPWARD DYNEX [ 200X ]\n"
        "• TELEPORT PLAYER\n"
        "• UPCOMING AUTO TELEPORT\n"
        "• UPCOMING JUMP REVISER\n"
        "• LOCK POSITION\n"
        "• BASE BREAKER\n"
        "• GHOST HACK\n"
        "• SHAKE KILL\n\n"
        "**GLOBAL FEATURES**\n"
        "• SPEED JOYSTICK\n"
        "• SPEED SCALER\n"
        "• NIGHT MODE\n"
        "• LOOK & EMOTE CHANGER\n"
        "• 11+ PREMIUM LOOK CHANGERS\n"
        "• 7+ PREMIUM EMOTE CHANGERS\n"
        "• MORE THAN 40+ FEATURES\n\n"
        "**SETTING FEATURES**\n"
        "• RESET GUEST\n"
        "• KEYBIND SUPPORT\n"
        "• TOPMOST SUPPORT\n"
        "• THEME SUPPORT\n"
        "• MORE THAN 40+ FEATURES\n\n"
        "**PRICES :**\n"
        "• **1 DAYS - 140 INR | 1.60 USD**\n"
        "• **7 DAYS - 600 INR | 7 USD**\n"
        "• **30 DAYS - 1800 INR | 20 USD**\n"
        "• **LIFETIME - 4500 INR | 40 USD**\n\n"
        "**FOR PURCHASE** <#1550562248932724756>"
    )

    embed = discord.Embed(
        description=description_text,
        color=discord.Color.from_rgb(0, 162, 255),
    )

    banner_url = "https://media.discordapp.net/attachments/1529086631536234637/1530160532974211283/standard_1.gif"
    embed.set_image(url=banner_url)

    await ctx.send(embed=embed)


# ================= RUN SERVER & BOT =================
if __name__ == "__main__":
    keep_alive()  # Web server start karega
    token = os.environ.get("DISCORD_TOKEN") or os.getenv("TOKEN")
    if token:
        bot.run(token)
    else:
        print("❌ Token nahi mila!")
