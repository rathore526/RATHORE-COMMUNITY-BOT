import os
from flask import Flask
from threading import Thread
import datetime
import discord
from discord.ext import commands
import asyncio
import re
import io

# ================= FLASK KEEP ALIVE SERVER =================
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ================= DISCORD BOT SETUP =================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ================= CONFIGURATION =================
WELCOME_CHANNEL_ID = 1548746560626499636
AUDIT_LOG_CHANNEL_ID = 1548751930665340989   # Server logs ID / Ticket Transcripts
JOIN_LEAVE_CHANNEL_ID = 1548752079248691200  # Join-Leave logs ID
MOD_LOG_CHANNEL_ID = 1548751987695296664     # Mod-logs ID
AUTO_ROLE_NAME = "→ Rathore Community"
BAD_WORDS = ["rathore ke maa ke chut", "rathore randi", "rathore ke mummy", "rathore"]
TARGET_USER_ID = 1529085822551326862  # Target / Owner ID with special security privileges

# 💳 PAYMENT DETAILS CONFIGURATION
UPI_ID = "9818940367@fam"
UPI_NAME = "Krishna"
UPI_QR_URL = "https://cdn.discordapp.com/attachments/1548769995582869554/1550484011082850384/Screenshot_20260809-233235_FamApp.jpg?ex=6aae8042&is=6aad2ec2&hm=b165e0cfbae4a37e6627b329dcea72fbb2f0573703396fb4ff5b1f06307a9e1f&"

BINANCE_ID = "123456789"
BINANCE_NAME = "Rathore X Crypto"
BINANCE_QR_URL = "https://your-image-url.com/binance_qr.png"

# 🖼️ BANNER IMAGES LINKS
BANNER_IMAGE_URL = "https://cdn.discordapp.com/attachments/1529086631536234637/1548913864811479070/WLCM.gif?ex=6aad6732&is=6aac15b2&hm=33843e4ad7963cecc2ed66f3e05c7f36db641f4cc2a45e120e2ddbdd3d0288ff&"
PURCHASE_BANNER_URL = "https://media.discordapp.net/attachments/1548769995582869554/1550471469119574067/standard.gif?ex=6aae7494&is=6aad2314&hm=63659b85776fbed5f9a7bb2ed29587cc542062c55cc189e705f35996392d9497&=&width=640&height=360"
SUPPORT_BANNER_URL = "https://cdn.discordapp.com/attachments/1529086631536234637/1548903192644026489/standard_2.gif?ex=6aad5d42&is=6aac0bc2&hm=f3ec8787fc33990e65cb180fde4ba00a66b4bd0ad7084f297f145f23f1f1ce78&"
PAYMENT_BANNER_URL = "https://media.discordapp.net/attachments/1548769995582869554/1550488423511629914/standard_1.gif?ex=6aae845e&is=6aad32de&hm=6c150d2e91f7c55626853150851a4c029ba6372c705112e4ee222ca2c35caadf&="

# 🎫 TICKET CATEGORIES
PURCHASE_CATEGORY_NAME = "🎫┃𝘗𝘜𝘙𝘊𝘏𝘈𝘚𝘌-𝘏𝘌𝘙𝘌"
SUPPORT_CATEGORY_NAME = "🎟️┃𝘚𝘜𝘗𝘗𝘖𝘙𝘛"
PAYMENT_CATEGORY_NAME = "💳┃𝘗𝘈𝘠𝘔𝘌𝘕𝘛-𝘔𝘌𝘛𝘏𝘖𝘋"
# =================================================

# --- CLOSE TICKET BUTTON WITH TRANSCRIPT LOGGING ---
class CloseButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⚠️ Generating transcript & deleting ticket in 5 seconds...")

        # Audit Log me File Save karne ka System
        log_channel = interaction.guild.get_channel(1550511155464773652)
        if log_channel:
            messages = []
            async for msg in interaction.channel.history(limit=500, oldest_first=True):
                timestamp = msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
                messages.append(f"[{timestamp}] {msg.author} ({msg.author.id}): {msg.content}")

            transcript_text = "\n".join(messages)
            file_data = io.BytesIO(transcript_text.encode('utf-8'))
            discord_file = discord.File(fp=file_data, filename=f"transcript-{interaction.channel.name}.txt")

            embed = discord.Embed(
                title="📄 Ticket Transcript Log",
                description=f"**Ticket Name:** {interaction.channel.name}\n**Closed By:** {interaction.user.mention}",
                color=discord.Color.red()
            )
            await log_channel.send(embed=embed, file=discord_file)

        await asyncio.sleep(5)
        await interaction.channel.delete()

# --- 1. PURCHASE TICKET DROPDOWN ---
class PurchaseDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Buy Cheat / Service", description="Open ticket to buy cheats or products", emoji="🛒"),
            discord.SelectOption(label="Inquire Price / Support", description="Ask details about pricing", emoji="💵"),
        ]
        super().__init__(
            placeholder="Select a purchase option",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="purchase_dropdown_menu"
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        member = interaction.user
        selected_option = self.values[0]

        category = discord.utils.get(guild.categories, name=PURCHASE_CATEGORY_NAME)
        if not category:
            category = await guild.create_category(PURCHASE_CATEGORY_NAME)

        channel_name = f"buy-{member.name.lower()}"
        existing_channel = discord.utils.get(guild.channels, name=channel_name)

        if existing_channel:
            await interaction.followup.send(f"❌ Aapka ticket pehle se khula hai: {existing_channel.mention}", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title=f"🛒 Purchase Ticket: {selected_option}",
            description=f"Hello {member.mention}, welcome! Please wait for staff to share product details or type your query.",
            color=discord.Color.from_rgb(88, 101, 242)
        )

        await ticket_channel.send(content=f"{member.mention}", embed=embed, view=CloseButton())
        await interaction.followup.send(f"✅ Aapka purchase ticket ban gaya hai: {ticket_channel.mention}", ephemeral=True)

class PurchaseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PurchaseDropdown())

# --- 2. PAYMENT METHOD DROPDOWN ---
class PaymentDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Indian Payment (UPI / QR)", description="Pay via PhonePe, Paytm, GPay, UPI QR", emoji="🇮🇳"),
            discord.SelectOption(label="Binance / Crypto Payment", description="Pay via Binance Pay, USDT, Crypto", emoji="🟡"),
        ]
        super().__init__(
            placeholder="Select your preferred Payment Method",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="payment_dropdown_menu"
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        member = interaction.user
        selected_option = self.values[0]

        prefix = "upi" if "Indian Payment" in selected_option else "crypto"

        category = discord.utils.get(guild.categories, name=PAYMENT_CATEGORY_NAME)
        if not category:
            category = await guild.create_category(PAYMENT_CATEGORY_NAME)

        channel_name = f"{prefix}-{member.name.lower()}"
        existing_channel = discord.utils.get(guild.channels, name=channel_name)

        if existing_channel:
            await interaction.followup.send(f"❌ Aapka payment ticket pehle se khula hai: {existing_channel.mention}", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title=f"💳 Payment Ticket: {selected_option}",
            description=f"Hello {member.mention}, welcome!\n\nStaff will send payment details shortly. You can also use `!upi` or `!binance` command here.",
            color=discord.Color.gold()
        )

        await ticket_channel.send(content=f"{member.mention}", embed=embed, view=CloseButton())
        await interaction.followup.send(f"✅ Aapka payment ticket ban gaya hai: {ticket_channel.mention}", ephemeral=True)

class PaymentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PaymentDropdown())

# --- 3. SUPPORT TICKET DROPDOWN ---
class SupportDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="General Support", description="Get general help from staff team", emoji="❓"),
            discord.SelectOption(label="Technical Issue", description="Get help with errors or issues", emoji="⚙️"),
            discord.SelectOption(label="Report Player/Issue", description="Report a member or server issue", emoji="🚨"),
        ]
        super().__init__(
            placeholder="Select a support option",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="support_dropdown_menu"
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        member = interaction.user
        selected_option = self.values[0]

        category = discord.utils.get(guild.categories, name=SUPPORT_CATEGORY_NAME)
        if not category:
            category = await guild.create_category(SUPPORT_CATEGORY_NAME)

        channel_name = f"support-{member.name.lower()}"
        existing_channel = discord.utils.get(guild.channels, name=channel_name)

        if existing_channel:
            await interaction.followup.send(f"❌ Aapka support ticket pehle se khula hai: {existing_channel.mention}", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title=f"🛠️ Support Ticket: {selected_option}",
            description=f"Hello {member.mention}, welcome to Support! Please explain your issue, and our staff team will assist you shortly.",
            color=discord.Color.from_rgb(57, 255, 20)
        )

        await ticket_channel.send(content=f"{member.mention}", embed=embed, view=CloseButton())
        await interaction.followup.send(f"✅ Aapka support ticket ban gaya hai: {ticket_channel.mention}", ephemeral=True)

class SupportView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SupportDropdown())

# --- BOT EVENTS ---
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

    # Welcome Message
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
            color=discord.Color.from_rgb(0, 162, 255)
        )
        if BANNER_IMAGE_URL:
            embed.set_image(url=BANNER_IMAGE_URL)
        await channel.send(content=content_text, embed=embed)

    # Join Log Message
    log_channel = bot.get_channel(JOIN_LEAVE_CHANNEL_ID)
    if log_channel:
        log_embed = discord.Embed(
            title="📥 Member Joined",
            description=f"{member.mention} ({member.name}) ne server join kiya!",
            color=discord.Color.green()
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
            color=discord.Color.red()
        )
        log_embed.set_thumbnail(url=member.display_avatar.url)
        await log_channel.send(embed=log_embed)

# --- AUDIT LOG EVENTS ---
@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    log_channel = bot.get_channel(AUDIT_LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(title="🗑️ Message Deleted", color=discord.Color.red())
        embed.add_field(name="User", value=message.author.mention, inline=True)
        embed.add_field(name="Channel", value=message.channel.mention, inline=True)
        embed.add_field(name="Content", value=message.content or "No Text / Attachment", inline=False)
        await log_channel.send(embed=embed)

@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content:
        return
    log_channel = bot.get_channel(AUDIT_LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(title="✏️ Message Edited", color=discord.Color.gold())
        embed.add_field(name="User", value=before.author.mention, inline=True)
        embed.add_field(name="Channel", value=before.channel.mention, inline=True)
        embed.add_field(name="Before", value=before.content, inline=False)
        embed.add_field(name="After", value=after.content, inline=False)
        await log_channel.send(embed=embed)

@bot.event
async def on_member_update(before, after):
    if before.roles != after.roles:
        log_channel = bot.get_channel(AUDIT_LOG_CHANNEL_ID)
        if not log_channel:
            return

        added_roles = [role for role in after.roles if role not in before.roles]
        removed_roles = [role for role in before.roles if role not in after.roles]

        for role in added_roles:
            embed = discord.Embed(title="🛡️ Role Given to Member", color=discord.Color.blue())
            embed.add_field(name="User", value=after.mention, inline=True)
            embed.add_field(name="Role Added", value=role.mention, inline=True)
            embed.set_thumbnail(url=after.display_avatar.url)
            await log_channel.send(embed=embed)

        for role in removed_roles:
            embed = discord.Embed(title="🛡️ Role Removed from Member", color=discord.Color.dark_orange())
            embed.add_field(name="User", value=after.mention, inline=True)
            embed.add_field(name="Role Removed", value=role.name, inline=True)
            embed.set_thumbnail(url=after.display_avatar.url)
            await log_channel.send(embed=embed)

@bot.event
async def on_guild_role_create(role):
    log_channel = bot.get_channel(AUDIT_LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(title="✨ New Role Created", color=discord.Color.green())
        embed.add_field(name="Role Name", value=role.name, inline=True)
        embed.add_field(name="Role ID", value=role.id, inline=True)
        await log_channel.send(embed=embed)

@bot.event
async def on_guild_role_delete(role):
    log_channel = bot.get_channel(AUDIT_LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(title="🗑️ Role Deleted", color=discord.Color.red())
        embed.add_field(name="Role Name", value=role.name, inline=True)
        await log_channel.send(embed=embed)

@bot.event
async def on_guild_channel_create(channel):
    log_channel = bot.get_channel(AUDIT_LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(title="📁 New Channel Created", color=discord.Color.green())
        embed.add_field(name="Channel Name", value=channel.name, inline=True)
        embed.add_field(name="Type", value=str(channel.type).capitalize(), inline=True)
        embed.add_field(name="Channel Mention", value=channel.mention if hasattr(channel, 'mention') else channel.name, inline=False)
        await log_channel.send(embed=embed)

@bot.event
async def on_guild_channel_delete(channel):
    log_channel = bot.get_channel(AUDIT_LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(title="🗑️ Channel Deleted", color=discord.Color.red())
        embed.add_field(name="Channel Name", value=channel.name, inline=True)
        embed.add_field(name="Type", value=str(channel.type).capitalize(), inline=True)
        await log_channel.send(embed=embed)

# --- MOD LOGS ---
@bot.event
async def on_member_ban(guild, user):
    mod_channel = bot.get_channel(MOD_LOG_CHANNEL_ID)
    if mod_channel:
        embed = discord.Embed(title="🔨 Member Banned (Discord UI)", color=discord.Color.red())
        embed.add_field(name="User", value=f"{user.mention} ({user.name})", inline=False)
        embed.set_thumbnail(url=user.display_avatar.url)
        await mod_channel.send(embed=embed)

@bot.event
async def on_member_unban(guild, user):
    mod_channel = bot.get_channel(1548751987695296664)
    if mod_channel:
        embed = discord.Embed(title="🔓 Member Unbanned", color=discord.Color.green())
        embed.add_field(name="User", value=f"{user.mention} ({user.name})", inline=False)
        embed.set_thumbnail(url=user.display_avatar.url)
        await mod_channel.send(embed=embed)

# --- AUTO MODERATION & TARGET USER SECURITY ---
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # SIRF AAP (Target User ID) hi commands run kar sakte hain
    if message.author.id != 1529085822551326862:
        # Agar koi aur command (! prefix) run karne ki koshish kare toh block kar do
        if message.content.startswith(bot.command_prefix):
            await message.channel.send(f"⚠️ {message.author.mention}, aapko yeh bot commands use karne ki permission nahi hai!", delete_after=5)
            return

        # Normal users ke liye Automod Checks
        msg_content = message.content.lower()

        # 1. Invite Link Check
        discord_invite_pattern = r"(discord\.gg|discord\.com/invite)/[a-zA-Z0-9]+"
        if re.search(discord_invite_pattern, msg_content):
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, invite links allowed nahi hain!", delete_after=5)
            except Exception as e:
                print(f"Delete Error: {e}")
            return

        # 2. Owner Mention / Ping Check
        user_tagged = any(user.id == TARGET_USER_ID for user in message.mentions)
        if user_tagged or message.mention_everyone:
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, owner ko ping nahi kar sakte!", delete_after=5)
            except Exception as e:
                print(f"Delete Error: {e}")
            return

        # 3. Bad Words Check
        for word in BAD_WORDS:
            if word in msg_content:
                try:
                    await message.delete()
                    await message.channel.send(f"⚠️ {message.author.mention}, bad words allowed nahi hain!", delete_after=5)
                except Exception as e:
                    print(f"Delete Error: {e}")
                return

    # Agar Message Aapka (Owner ka) hai, tabhi Command Process Hoga
    await bot.process_commands(message)

# --- COMMANDS ---

@bot.command()
@commands.has_permissions(administrator=True)
async def purchasepanel(ctx):
    await ctx.message.delete()
    description_text = (
        "Welcome to **RATHORE X CHEATS**, your trusted source for premium modifications, tools, and exclusive services. Create a ticket below to receive fast support, purchase assistance, or answers to your questions.\n\n"
        "⠀\n"
        "📌 **RULES**\n"
        "⠀\n"
        "• Create tickets only for purchases, support, or legitimate inquiries.\n"
        "⠀\n"
        "• Creating tickets for fun, trolling, or wasting staff time will result in a ban.\n"
        "⠀\n"
        "• All prices are listed publicly. Do not create tickets to negotiate or bargain.\n"
        "⠀\n"
        "• Be respectful to staff members at all times.\n"
        "⠀\n"
        "• Do not spam, ping staff repeatedly, or create multiple tickets for the same issue.\n"
        "⠀\n"
        "• Payments must be completed through approved methods only.\n\n"
        "⠀\n"
        "📌 **REGRAS**\n"
        "⠀\n"
        "• Crie tickets apenas para compras, suporte ou dúvidas legítimas.\n"
        "⠀\n"
        "• Criar tickets por diversão, trollagem ou para desperdiçar o tempo da equipe resultará em banimento.\n"
        "⠀\n"
        "• Todos os preços já estão listados. Não abra tickets para negociar valores.\n"
        "⠀\n"
        "• Respeite os membros da equipe em todos os momentos.\n"
        "⠀\n"
        "• Não envie spam, mencione a equipe repetidamente ou crie vários tickets para o mesmo problema.\n"
        "⠀\n"
        "• Os pagamentos devem ser realizados apenas pelos métodos aprovados.\n\n"
        "⠀\n"
        "⠀\n"
        "🔥 **Why Choose RATHORE X CHEATS !!**\n"
        "⠀\n"
        "✓ Fast Support\n"
        "⠀\n"
        "✓ Secure Transactions\n"
        "⠀\n"
        "✓ Premium Quality Services\n"
        "⠀\n"
        "✓ Trusted Community\n"
        "⠀\n"
        "✓ Professional Assistance\n\n"
        "⠀\n"
        "Click the button below to create a ticket and get started.\n\n"
        "⠀\n"
        "👑 **RATHORE X CHEATS @2026 | by RATHORE !! |**"
    )
    embed = discord.Embed(description=description_text, color=discord.Color.from_rgb(88, 101, 242))
    embed.set_footer(text="Powered by Owner 1nonlyrathore8")
    if PURCHASE_BANNER_URL:
        embed.set_image(url=PURCHASE_BANNER_URL)
    await ctx.send(embed=embed, view=PurchaseView())

@bot.command()
@commands.has_permissions(administrator=True)
async def paymentpanel(ctx):
    await ctx.message.delete()
    description_text = (
        "💳 **RATHORE X — PAYMENT METHODS**\n"
        "\n"
        "🔐 **SELECT YOUR PREFERRED PAYMENT METHOD**\n"
        "⠀\n"
        "Choose any available payment option below to receive the complete payment details.\n\n"
        "⠀\n"
        "After completing your payment, upload/send your payment screenshot for verification.\n\n"
        "⠀\n"
        "🇮🇳 **INDIAN PAYMENT METHODS**\n"
        "⠀\n"
        "• 📱 PhonePe\n"
        "⠀\n"
        "• 🟢 Google Pay\n"
        "⠀\n"
        "• 🔵 Paytm\n"
        "⠀\n"
        "• 🔳 UPI QR\n\n"
        "⠀\n"
        "🟡 **CRYPTO PAYMENT METHODS**\n"
        "⠀\n"
        "• 🟡 Binance Pay\n"
        "⠀\n"
        "• 💰 USDT — TRC20\n"
        "⠀\n"
        "• 💰 USDT — BEP20\n"
        "⠀\n"
        "\n"
        "📌 **PAYMENT INSTRUCTIONS**\n\n"
        "⠀\n"
        "1. Select your preferred payment method.\n"
        "⠀\n"
        "2. Complete the payment using the provided details.\n"
        "⠀\n"
        "3. Take a clear screenshot of the successful payment.\n"
        "⠀\n"
        "4. Submit the screenshot for payment verification.\n"
        "⠀\n"
        "5. Wait for confirmation after your payment has been verified.\n\n"
        "⠀\n"
        "⚠️ **IMPORTANT:** Make sure the payment details are correct before sending any payment.\n"
        "⠀\n"
        "\n"
        "🔥 **RATHORE X CHEATS @2026**\n"
        "⠀\n"
        "👑 **POWERED BY RATHORE !!**"
    )
    embed = discord.Embed(description=description_text, color=discord.Color.gold())
    embed.set_footer(text="Powered by Owner 1nonlyrathore8")
    if PAYMENT_BANNER_URL:
        embed.set_image(url=PAYMENT_BANNER_URL)
    await ctx.send(embed=embed, view=PaymentView())

@bot.command()
@commands.has_permissions(administrator=True)
async def supportpanel(ctx):
    await ctx.message.delete()
    description_text = (
        "🛠️ **RATHORE X CHEATS — SUPPORT TICKET**\n"
        "⠀\n"
        "Need help? Our support team is here to assist you with technical issues, account problems, product questions, or general inquiries.\n\n"
        "⠀\n"
        "📌 **BEFORE CREATING A TICKET**\n"
        "⠀\n"
        "• Check the FAQ and available guides first.\n"
        "⠀\n"
        "• Make sure your issue has not already been answered.\n"
        "⠀\n"
        "• Gather any screenshots or error messages that may help our staff assist you faster.\n\n"
        "⠀\n"
        "⠀\n"
        "📌 **SUPPORT RULES**\n"
        "⠀\n"
        "• Open tickets only for genuine support requests.\n"
        "⠀\n"
        "• Clearly explain your issue and provide relevant details.\n"
        "⠀\n"
        "• Be respectful and patient while waiting for a response.\n"
        "⠀\n"
        "• Do not spam messages, mentions, or create multiple tickets for the same issue.\n"
        "⠀\n"
        "• False reports, trolling, or misuse of the support system may result in a ban.\n\n"
        "⠀\n"
        "📌 **REGRAS DE SUPORTE**\n"
        "⠀\n"
        "• Abra tickets apenas para solicitações de suporte legítimas.\n"
        "⠀\n"
        "• Explique claramente seu problema e forneça detalhes relevantes.\n"
        "⠀\n"
        "• Seja respeitoso e paciente enquanto aguarda uma resposta.\n"
        "⠀\n"
        "• Não envie spam, marque a equipe repetidamente ou crie vários tickets para o mesmo problema.\n"
        "⠀\n"
        "• Relatórios falsos, trollagem ou abuso do sistema de suporte podem resultar em banimento.\n\n"
        "⠀\n"
        "🔥 **RATHORE X CHEATS SUPPORT**\n"
        "⠀\n"
        "✓ Technical Assistance\n"
        "⠀\n"
        "✓ Installation Help\n"
        "⠀\n"
        "✓ Account Support\n"
        "⠀\n"
        "✓ Product Information\n"
        "⠀\n"
        "✓ General Questions\n\n"
        "⠀\n"
        "Create a ticket below and a staff member will assist you as soon as possible.\n\n"
        "⠀\n"
        "👑 **RATHORE X CHEATS @2026 | by RATHORE !! |**"
    )
    embed = discord.Embed(description=description_text, color=discord.Color.from_rgb(57, 255, 20))
    embed.set_footer(text="Powered by Owner 1nonlyrathore8")
    if SUPPORT_BANNER_URL:
        embed.set_image(url=SUPPORT_BANNER_URL)
    await ctx.send(embed=embed, view=SupportView())

@bot.command()
@commands.has_permissions(administrator=True)
async def upi(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        title="💳 Indian Payment Details (UPI / QR)",
        description=f"Send payment to the details below and share the **screenshot + Transaction ID** in this ticket.\n\n"
                    f"🔹 **UPI ID:** `{UPI_ID}`\n"
                    f"🔹 **Payee Name:** {UPI_NAME}\n\n"
                    f"⚠️ *Payment complete hone ke baad screenshot zaroor bhejein!*",
        color=discord.Color.green()
    )
    if UPI_QR_URL:
        embed.set_image(url=UPI_QR_URL)
    embed.set_footer(text="Rathore X Cheats | Secure Payment System")
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def binance(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        title="🟡 Binance / Crypto Payment Details",
        description=f"Send payment using Binance Pay ID or Crypto address below. Share the **Transaction Hash / Screenshot** after completion.\n\n"
                    f"🔹 **Binance Pay ID / Address:** `{BINANCE_ID}`\n"
                    f"🔹 **Account Name:** {BINANCE_NAME}\n\n"
                    f"⚠️ *Double check the address before sending crypto!*",
        color=discord.Color.gold()
    )
    if BINANCE_QR_URL and BINANCE_QR_URL != "https://your-image-url.com/binance_qr.png":
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
        await ctx.send(f"🔒 **{role.name}** role ke liye yeh channel lock kar diya gaya hai!")
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
        await ctx.send(f"🔓 **{role.name}** role ke liye yeh channel unlock kar diya gaya hai!")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}", delete_after=5)

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 {amount} messages delete kar diye gaye!", delete_after=3)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Koyi reason nahi diya"):
    await member.kick(reason=reason)
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
async def ban(ctx, member: discord.Member, *, reason="Rule break kiya"):
    await member.ban(reason=reason)
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
    await member.timeout(duration, reason=reason)
    await ctx.send(f"⏳ {member.mention} ko {minutes} minute ke liye timeout kar diya gaya.")

    mod_channel = bot.get_channel(MOD_LOG_CHANNEL_ID)
    if mod_channel:
        embed = discord.Embed(title="⏳ Member Timed Out", color=discord.Color.gold())
        embed.add_field(name="User", value=f"{member.mention} ({member.name})", inline=True)
        embed.add_field(name="Duration", value=f"{minutes} Minutes", inline=True)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        await mod_channel.send(embed=embed)

# Keep Alive Run
keep_alive()

# Run Bot
bot.run(os.getenv("TOKEN"))
