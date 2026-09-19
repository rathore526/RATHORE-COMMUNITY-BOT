import asyncio
import datetime
import io
import os
import re
from threading import Thread

import discord
from discord.ext import commands
from flask import Flask

# ================= FLASK KEEP ALIVE SERVER =================
app = Flask("")


@app.route("/")
def home():
    return "Bot is alive!"


def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


def keep_alive():
    t = Thread(target=run)
    t.start()


# ================= DISCORD BOT SETUP =================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.auto_moderation = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    max_messages=10000,
    partials=[discord.Partials.MESSAGE, discord.Partials.CHANNEL, discord.Partials.REACTION],
)

# ================= CONFIGURATION =================
WELCOME_CHANNEL_ID = 1548746560626499636
AUDIT_LOG_CHANNEL_ID = 1550511155464773652
JOIN_LEAVE_CHANNEL_ID = 1548752079248691200  # Join-Leave logs ID
MOD_LOG_CHANNEL_ID = 1548751987695296664  # Mod-logs ID
TICKET_LOG_CHANNEL_ID = 1550532272011214919  # Ticket activity logs
TICKET_TRANSCRIPT_LOG_ID = 1550822114238533773  # Ticket transcript logs

# 📌 TICKET OPEN CHANNELS
PURCHASE_TICKET_CHANNEL_ID = 1550532272011214919
SUPPORT_TICKET_CHANNEL_ID = 1550532272011214919
PAYMENT_TICKET_CHANNEL_ID = 1550532272011214919

AUTO_ROLE_NAME = "→ Rathore Community"
BAD_WORDS = ["rathore ke maa ke chut", "rathore randi", "rathore ke mummy"]
TARGET_USER_ID = 1529085822551326862  # Owner/Target User ID

# 💳 PAYMENT DETAILS CONFIGURATION
UPI_ID = "9818940367@fam"
UPI_NAME = "Krishna"
UPI_QR_URL = "https://cdn.discordapp.com/attachments/1548769995582869554/1550484011082850384/Screenshot_20260809-233235_FamApp.jpg"

BINANCE_ID = "123456789"
BINANCE_NAME = "Rathore X Crypto"
BINANCE_QR_URL = "https://your-image-url.com/binance_qr.png"

# 🖼️ BANNER IMAGES LINKS
BANNER_IMAGE_URL = "https://cdn.discordapp.com/attachments/1529086631536234637/1548913864811479070/WLCM.gif"
PURCHASE_BANNER_URL = "https://media.discordapp.net/attachments/1548769995582869554/1550471469119574067/standard.gif"
SUPPORT_BANNER_URL = "https://cdn.discordapp.com/attachments/1529086631536234637/1548903192644026489/standard_2.gif"
PAYMENT_BANNER_URL = "https://media.discordapp.net/attachments/1548769995582869554/1550488423511629914/standard_1.gif"

# 🎫 TICKET CATEGORIES
PURCHASE_CATEGORY_NAME = "🎫┃𝘗𝘜𝘙𝘊𝘏𝘈𝘚𝘌-𝘏𝘌𝘙𝘌"
SUPPORT_CATEGORY_NAME = "🎟️┃𝘚𝘜𝘗𝘗𝘖𝘙𝘛"
PAYMENT_CATEGORY_NAME = "💳┃𝘗𝘈𝘠𝘔𝘌𝘕𝘛-𝘔𝘌𝘛𝘏𝘖𝘋"

# ================= VIEWS & BUTTONS =================


class CloseButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Close Ticket 🔒",
        style=discord.ButtonStyle.red,
        custom_id="close_ticket_btn",
    )
    async def close_ticket(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "🔒 Ticket 5 seconds me close ho raha hai...", ephemeral=False
        )
        await asyncio.sleep(5)
        await interaction.channel.delete()


class PurchaseDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Buy Cheat / Service",
                description="Open ticket to buy cheats or products",
                emoji="🛒",
            ),
            discord.SelectOption(
                label="Inquire Price / Support",
                description="Ask details about pricing",
                emoji="💵",
            ),
        ]
        super().__init__(
            placeholder="Select a purchase option",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="purchase_dropdown_menu",
        )

    async def callback(self, interaction: discord.Interaction):
        selected_option = self.values[0]
        guild = interaction.guild

        category = discord.utils.get(
            guild.categories, name=PURCHASE_CATEGORY_NAME
        )
        if not category:
            category = await guild.create_category(PURCHASE_CATEGORY_NAME)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                read_messages=False
            ),
            interaction.user: discord.PermissionOverwrite(
                read_messages=True, send_messages=True
            ),
            guild.me: discord.PermissionOverwrite(
                read_messages=True, send_messages=True
            ),
        }

        ticket_channel = await guild.create_text_channel(
            name=f"purchase-{interaction.user.name.lower()}",
            overwrites=overwrites,
            category=category,
        )

        await interaction.response.send_message(
            f"✅ Ticket created: {ticket_channel.mention}", ephemeral=True
        )
        await ticket_channel.send(
            f"Welcome {interaction.user.mention}! Selected Option: **{selected_option}**",
            view=CloseButton(),
        )

        # Log Message Send
        log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="🎟️ New Purchase Ticket Opened",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow(),
            )
            embed.add_field(
                name="👤 Opened By",
                value=f"{interaction.user.mention} (`{interaction.user.id}`)",
                inline=False,
            )
            embed.add_field(
                name="🏷️ Option Selected", value=selected_option, inline=True
            )
            embed.add_field(
                name="📂 Ticket Channel",
                value=ticket_channel.mention,
                inline=True,
            )
            embed.set_footer(text=f"User ID: {interaction.user.id}")

            await log_channel.send(
                content=f"<@{TARGET_USER_ID}>", embed=embed
            )


class PurchaseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PurchaseDropdown())


class PaymentDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Indian Payment (UPI / QR)",
                description="Pay via PhonePe, Paytm, GPay, UPI QR",
                emoji="🇮🇳",
            ),
            discord.SelectOption(
                label="Binance / Crypto Payment",
                description="Pay via Binance Pay, USDT, Crypto",
                emoji="🟡",
            ),
        ]
        super().__init__(
            placeholder="Select your preferred Payment Method",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="payment_dropdown_menu",
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        member = interaction.user
        selected_option = self.values[0]

        prefix = "upi" if "Indian Payment" in selected_option else "crypto"

        category = discord.utils.get(
            guild.categories, name=PAYMENT_CATEGORY_NAME
        )
        if not category:
            category = await guild.create_category(PAYMENT_CATEGORY_NAME)

        channel_name = f"{prefix}-{member.name.lower()}"
        existing_channel = discord.utils.get(
            guild.channels, name=channel_name
        )

        if existing_channel:
            await interaction.followup.send(
                f"❌ Aapka payment ticket pehle se khula hai: {existing_channel.mention}",
                ephemeral=True,
            )
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                read_messages=False
            ),
            member: discord.PermissionOverwrite(
                read_messages=True, send_messages=True
            ),
            guild.me: discord.PermissionOverwrite(
                read_messages=True, send_messages=True
            ),
        }

        ticket_channel = await guild.create_text_channel(
            name=channel_name, category=category, overwrites=overwrites
        )

        embed = discord.Embed(
            title=f"💳 Payment Ticket: {selected_option}",
            description=f"Hello {member.mention}, welcome!\n\nStaff will send payment details shortly.",
            color=discord.Color.gold(),
        )

        await ticket_channel.send(
            content=f"{member.mention}", embed=embed, view=CloseButton()
        )
        await interaction.followup.send(
            f"✅ Aapka payment ticket ban gaya hai: {ticket_channel.mention}",
            ephemeral=True,
        )

        log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="💳 New Payment Ticket Opened",
                color=discord.Color.gold(),
                timestamp=discord.utils.utcnow(),
            )
            log_embed.add_field(
                name="👤 Opened By",
                value=f"{member.mention} (`{member.id}`)",
                inline=False,
            )
            log_embed.add_field(
                name="🏷️ Option Selected", value=selected_option, inline=True
            )
            log_embed.add_field(
                name="📂 Ticket Channel",
                value=ticket_channel.mention,
                inline=True,
            )
            log_embed.set_footer(text=f"User ID: {member.id}")

            await log_channel.send(
                content=f"<@{TARGET_USER_ID}>", embed=log_embed
            )


class PaymentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PaymentDropdown())


class SupportDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="General Support",
                description="Get general help from staff team",
                emoji="❓",
            ),
            discord.SelectOption(
                label="Technical Issue",
                description="Get help with errors or issues",
                emoji="⚙️",
            ),
            discord.SelectOption(
                label="Report Player/Issue",
                description="Report a member or server issue",
                emoji="🚨",
            ),
        ]
        super().__init__(
            placeholder="Select a support option",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="support_dropdown_menu",
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        member = interaction.user
        selected_option = self.values[0]

        category = discord.utils.get(
            guild.categories, name=SUPPORT_CATEGORY_NAME
        )
        if not category:
            category = await guild.create_category(SUPPORT_CATEGORY_NAME)

        channel_name = f"support-{member.name.lower()}"
        existing_channel = discord.utils.get(
            guild.channels, name=channel_name
        )

        if existing_channel:
            await interaction.followup.send(
                f"❌ Aapka support ticket pehle se khula hai: {existing_channel.mention}",
                ephemeral=True,
            )
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                read_messages=False
            ),
            member: discord.PermissionOverwrite(
                read_messages=True, send_messages=True
            ),
            guild.me: discord.PermissionOverwrite(
                read_messages=True, send_messages=True
            ),
        }

        ticket_channel = await guild.create_text_channel(
            name=channel_name, category=category, overwrites=overwrites
        )

        embed = discord.Embed(
            title=f"🛠️ Support Ticket: {selected_option}",
            description=f"Hello {member.mention}, welcome to Support! Please explain your issue, and our staff team will assist you shortly.",
            color=discord.Color.from_rgb(57, 255, 20),
        )

        await ticket_channel.send(
            content=f"{member.mention}", embed=embed, view=CloseButton()
        )
        await interaction.followup.send(
            f"✅ Aapka support ticket ban gaya hai: {ticket_channel.mention}",
            ephemeral=True,
        )

        log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="🛠️ New Support Ticket Opened",
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow(),
            )
            log_embed.add_field(
                name="👤 Opened By",
                value=f"{member.mention} (`{member.id}`)",
                inline=False,
            )
            log_embed.add_field(
                name="🏷️ Option Selected", value=selected_option, inline=True
            )
            log_embed.add_field(
                name="📂 Ticket Channel",
                value=ticket_channel.mention,
                inline=True,
            )
            log_embed.set_footer(text=f"User ID: {member.id}")

            await log_channel.send(
                content=f"<@{TARGET_USER_ID}>", embed=log_embed
            )


class SupportView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SupportDropdown())


# ================= EVENTS =================


@bot.event
async def on_ready():
    bot.add_view(PurchaseView())
    bot.add_view(PaymentView())
    bot.add_view(SupportView())
    bot.add_view(CloseButton())
    print(f"🛡️ {bot.user} Rathore X Cheats Bot Online Hai!")


@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name=AUTO_ROLE_NAME)
    if role:
        try:
            await member.add_roles(role)
        except Exception as e:
            print(f"Role error: {e}")

    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        content_text = f"{member.mention} Welcome to **RATHORE COMMUNITY**!!!"
        embed_description = (
            "📌 | **<#1548747102799269959>**\n"
            "MAKE SURE YOU READ ALL THE RULES\n\n"
            "📢 | **<#1548747535147860098>**\n"
            "ALL THE ANNOUNCEMENT ARE THERE\n\n"
            "💬 | **<#1548759359402676244>**\n"
            "INTRODUCE YOURSELF HERE BY CHATTING IN GENERAL CHAT\n\n"
            "YOU HAVE A GOOD DAY IN **RATHORE COMMUNITY** !! AND THANKS FOR A PART OF OUR COMMUNITY"
        )
        embed = discord.Embed(
            description=embed_description,
            color=discord.Color.from_rgb(0, 162, 255),
        )
        if BANNER_IMAGE_URL:
            embed.set_image(url=BANNER_IMAGE_URL)
        await channel.send(content=content_text, embed=embed)

    log_channel = bot.get_channel(JOIN_LEAVE_CHANNEL_ID)
    if log_channel:
        log_embed = discord.Embed(
            title="📥 Member Joined",
            description=f"{member.mention} ({member.name}) ne server join kiya!",
            color=discord.Color.green(),
        )
        log_embed.set_thumbnail(url=member.display_avatar.url)
        await log_channel.send(embed=log_embed)


@bot.event
async def on_member_remove(member):
    log_channel = bot.get_channel(JOIN_LEAVE_CHANNEL_ID)
    if log_channel:
        log_embed = discord.Embed(
            title="📤 Member Left",
            description=f"**{member.name}** ne server chor diya hai.",
            color=discord.Color.red(),
        )
        log_embed.set_thumbnail(url=member.display_avatar.url)
        await log_channel.send(embed=log_embed)


# --- AUTO-MODERATION & COMMAND PROCESSOR ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    msg_content = message.content.lower()

    # 1. Invite Link Check
    discord_invite_pattern = r"(discord\.gg|discord\.com/invite)/[a-zA-Z0-9]+"
    if re.search(discord_invite_pattern, msg_content):
        try:
            await message.delete()
            await message.channel.send(
                f"⚠️ {message.author.mention}, invite links allowed nahi hain!",
                delete_after=5,
            )
        except Exception as e:
            print(f"Delete Error: {e}")
        return

    # 2. Owner Mention / Ping Check
    user_tagged = any(user.id == TARGET_USER_ID for user in message.mentions)
    if user_tagged or message.mention_everyone:
        try:
            await message.delete()
            await message.channel.send(
                f"⚠️ {message.author.mention}, owner ko ping nahi kar sakte!",
                delete_after=5,
            )
        except Exception as e:
            print(f"Delete Error: {e}")
        return

    # 3. Bad Words Check
    for word in BAD_WORDS:
        if word in msg_content:
            try:
                await message.delete()
                await message.channel.send(
                    f"⚠️ {message.author.mention}, bad words allowed nahi hain!",
                    delete_after=5,
                )
            except Exception as e:
                print(f"Delete Error: {e}")
            return

    await bot.process_commands(message)


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
        "✅ Purchase, Support aur Payment Teeno Ticket Panels Setup Ho Gaye Hain!"
    )


@bot.command()
@commands.has_permissions(administrator=True)
async def purchasepanel(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        title="🛒 RATHORE X CHEATS - PURCHASE",
        description="Select an option below to buy cheats or inquire about product pricing.",
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
        "Need help? Our support team is here to assist you with technical issues, account problems, or product questions.\n\n"
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
            f"🔓 **{role.name}** role ke liye yeh channel unlock kar diya gaya hai!"
        )
    except Exception as e:
        await ctx.send(f"❌ Error: {e}", delete_after=5)


@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(
        f"🧹 {amount} messages delete kar diye gaye!", delete_after=3
    )


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
    await ctx.send(
        f"⛔ {member.mention} ko BAN kar diya gaya. Reason: {reason}"
    )

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
            "❌ Main is user ko timeout nahi de sakta kyunki iska Role mere Bot Role se bada ya barabar hai!"
        )
        return

    duration = datetime.timedelta(minutes=minutes)
    try:
        await member.timeout(duration, reason=reason)
        await ctx.send(
            f"⏳ {member.mention} ko **{minutes} minute** ke liye timeout kar diya gaya."
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
            "❌ **Forbidden Error:** Mere paas `Moderate Members` permission nahi hai ya yeh user Admin hai."
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
