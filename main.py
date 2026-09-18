import os
from flask import Flask
from threading import Thread

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

import discord
from discord.ext import commands
import asyncio
import re

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ================= CONFIGURATION =================
WELCOME_CHANNEL_ID = 1548746560626499636
AUDIT_LOG_CHANNEL_ID = 1548751930665340989  # 👈 YAHAN APNI server-logs CHANNEL KI ID PASTE KAREIN
AUTO_ROLE_NAME = "→ Rathore Community"
BAD_WORDS = ["rathore ke maa ke chut", "rathore randi", "rathore ke mummy", "rathore"]
TARGET_USER_ID = 1529085822551326862

# 🖼️ BANNER IMAGES LINKS
BANNER_IMAGE_URL = "https://cdn.discordapp.com/attachments/1529086631536234637/1548913864811479070/WLCM.gif?ex=6aad6732&is=6aac15b2&hm=33843e4ad7963cecc2ed66f3e05c7f36db641f4cc2a45e120e2ddbdd3d0288ff&"
PURCHASE_BANNER_URL = "https://cdn.discordapp.com/attachments/1529086631536234637/1548900220979384360/standard_1.gif?ex=6aad5a7d&is=6aac08fd&hm=bc910c34be1892cd2d791bd139d5764273b2b2c912d0bdae26cde127b4bbebbf&"
SUPPORT_BANNER_URL = "https://cdn.discordapp.com/attachments/1529086631536234637/1548903192644026489/standard_2.gif?ex=6aad5d42&is=6aac0bc2&hm=f3ec8787fc33990e65cb180fde4ba00a66b4bd0ad7084f297f145f23f1f1ce78&"

# 🎫 TICKET CATEGORIES
PURCHASE_CATEGORY_NAME = "🎫┃𝘗𝘜𝘙𝘊𝘏𝘈𝘚𝘌-𝘏𝘌𝘙𝘌"
SUPPORT_CATEGORY_NAME = "🎟️┃𝘚𝘜𝘗𝘗𝘖𝘙𝘛"
# =================================================

# --- CLOSE TICKET BUTTON ---
class CloseButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⚠️ Yeh ticket 5 seconds mein delete ho jayega...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

# --- 1. PURCHASE TICKET DROPDOWN ---
class PurchaseDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Buy Cheats", description="Open ticket to buy premium cheats", emoji="🛒"),
            discord.SelectOption(label="Inquire Price", description="Ask details about cheat pricing", emoji="💵"),
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
            description=f"Hello {member.mention}, welcome to the purchase section! Staff team will assist you shortly.",
            color=discord.Color.from_rgb(88, 101, 242)
        )
        
        await ticket_channel.send(content=f"{member.mention}", embed=embed, view=CloseButton())
        await interaction.followup.send(f"✅ Aapka purchase ticket ban gaya hai: {ticket_channel.mention}", ephemeral=True)

class PurchaseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PurchaseDropdown())


# --- 2. SUPPORT TICKET DROPDOWN ---
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

    # Audit Log: Member Joined
    log_channel = bot.get_channel(AUDIT_LOG_CHANNEL_ID)
    if log_channel:
        log_embed = discord.Embed(title="📥 Member Joined", color=discord.Color.green())
        log_embed.add_field(name="User", value=f"{member.mention} ({member.name})", inline=False)
        await log_channel.send(embed=log_embed)

@bot.event
async def on_member_remove(member):
    # Audit Log: Member Left
    log_channel = bot.get_channel(AUDIT_LOG_CHANNEL_ID)
    if log_channel:
        log_embed = discord.Embed(title="📤 Member Left", color=discord.Color.dark_grey())
        log_embed.add_field(name="User", value=f"{member.name}", inline=False)
        await log_channel.send(embed=log_embed)

# --- AUDIT LOG EVENTS (DELETED & EDITED MESSAGES) ---
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

# --- AUTO MODERATION & MESSAGES ---
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.author.id == TARGET_USER_ID or (isinstance(message.author, discord.Member) and message.author.guild_permissions.administrator):
        await bot.process_commands(message)
        return

    msg_content = message.content.lower()

    discord_invite_pattern = r"(discord\.gg|discord\.com/invite)/[a-zA-Z0-9]+"
    if re.search(discord_invite_pattern, msg_content):
        try:
            await message.delete()
            await message.channel.send(f"⚠️ {message.author.mention}, server invite links bhejna allowed nahi hai!", delete_after=5)
        except Exception as e:
            print(f"Error: {e}")
        return

    user_tagged = any(user.id == TARGET_USER_ID for user in message.mentions)
    if user_tagged or message.mention_everyone:
        try:
            await message.delete()
            await message.channel.send(f"⚠️ **WARNING:** {message.author.mention}, aap owner ko ya `@everyone` ping nahi kar sakte!", delete_after=6)
        except Exception as e:
            print(f"Tag delete error: {e}")
        return

    for word in BAD_WORDS:
        if word in msg_content:
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, yeh word yahan use karna mana hai!", delete_after=5)
            except Exception as e:
                print(f"Error: {e}")
            return

    await bot.process_commands(message)

# --- COMMANDS ---

@bot.command()
@commands.has_permissions(administrator=True)
async def ticketpanel(ctx):
    await ctx.message.delete()
    description_text = (
        "**RATHORE X — PURCHASE CENTER**\n\n"
        "Welcome to RATHORE X CHEATS, your trusted source for premium modifications, tools, and exclusive services. Create a ticket below to receive fast support, purchase assistance, or answers to your questions.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━ **RULES**\n\n"
        "• Create tickets only for purchases, support, or legitimate inquiries.\n\n"
        "• Creating tickets for fun, trolling, or wasting staff time will result in a ban.\n\n"
        "• All prices are listed publicly. Do not create tickets to negotiate or bargain.\n\n"
        "• Be respectful to staff members at all times.\n\n"
        "• Do not spam, ping staff repeatedly, or create multiple tickets for the same issue.\n\n"
        "• Payments must be completed through approved methods only.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━ **Why Choose RATHORE X CHEATS !!**\n\n"
        "✓ Fast Support\n✓ Secure Transactions\n✓ Premium Quality Services\n✓ Trusted Community\n✓ Professional Assistance\n\n"
        "Click the dropdown menu below to create a ticket and get started.\n\n"
        "**RATHORE X CHEATS @2026 |by RATHORE !! |**"
    )
    embed = discord.Embed(description=description_text, color=discord.Color.from_rgb(88, 101, 242))
    embed.set_footer(text="Powered by Owner 1nonlyrathore8")
    if PURCHASE_BANNER_URL:
        embed.set_image(url=PURCHASE_BANNER_URL)
    await ctx.send(embed=embed, view=PurchaseView())

@bot.command()
@commands.has_permissions(administrator=True)
async def supportpanel(ctx):
    await ctx.message.delete()
    description_text = (
        "**RATHORE X CHEATS — SUPPORT TICKET**\n\n"
        "Need help? Our support team is here to assist you with technical issues, account problems, product questions, or general inquiries.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━ **SUPPORT RULES**\n\n"
        "• Open tickets only for genuine support requests.\n\n"
        "• Clearly explain your issue and provide relevant details.\n\n"
        "• Be respectful and patient while waiting for a response.\n\n"
        "• Do not spam messages, mentions, or create multiple tickets for the same issue.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━ **RATHORE X CHEATS SUPPORT**\n\n"
        "✓ Technical Assistance\n✓ Installation Help\n✓ Account Support\n✓ Product Information\n✓ General Questions\n\n"
        "Create a ticket below and a staff member will assist you as soon as possible.\n\n"
        "**RATHORE X CHEATS @2026 |by RATHORE !! |**"
    )
    embed = discord.Embed(description=description_text, color=discord.Color.from_rgb(57, 255, 20))
    embed.set_footer(text="Powered by Owner 1nonlyrathore8")
    if SUPPORT_BANNER_URL:
        embed.set_image(url=SUPPORT_BANNER_URL)
    await ctx.send(embed=embed, view=SupportView())

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

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Rule break kiya"):
    await member.ban(reason=reason)
    await ctx.send(f"⛔ {member.mention} ko BAN kar diya gaya. Reason: {reason}")

# Render ke liye safe token retrieval
keep_alive()
bot.run(os.getenv("TOKEN"))
