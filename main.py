import asyncio
from collections import defaultdict
import datetime
import io
import os
import re
from threading import Thread

import discord
from discord.ext import commands
from flask import Flask
from dotenv import load_dotenv

# --- SECURITY FIX ---
load_dotenv() # .env ya Render ke variables load karega

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ CRITICAL: DISCORD_TOKEN Render Environment me nahi mila!")
    exit()

OWNER_IDS_STR = os.getenv("OWNER_IDS", "")
OWNER_IDS = [int(x.strip()) for x in OWNER_IDS_STR.split(",") if x.strip().isdigit()]

# Flask keep-alive for Render
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is Alive & Secure!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

Thread(target=run_flask).start()

# ================= FLASK KEEP ALIVE SERVER =================
app = Flask('')


@app.route('/')
def home():
    return 'Bot is alive and running!'


def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)


def keep_alive():
    t = Thread(target=run)
    t.start()


# ================= DISCORD BOT SETUP =================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.auto_moderation = True

bot = commands.Bot(command_prefix='!', intents=intents, max_messages=10000)

# Local backup message cache to fix missing deleted message content
MESSAGE_CACHE = {}

# ================= CONFIGURATION =================
WELCOME_CHANNEL_ID = 1548746560626499636
AUDIT_LOG_CHANNEL_ID = 1548751930665340989
JOIN_LEAVE_CHANNEL_ID = 1548752079248691200
MOD_LOG_CHANNEL_ID = 1548751987695296664

# 🟢 Ticket OPEN Logs Channel
TICKET_LOG_CHANNEL_ID = 1550532272011214919

# 🔴 Ticket CLOSED Logs Channel & Transcript
TICKET_CLOSED_CHANNEL_ID = 1550812185679368283

AUTO_ROLE_NAME = '→ Rathore Community'
BAD_WORDS = ['rathore ke maa ke chut', 'rathore randi', 'rathore ke mummy']

# 👑 OWNER ONLY SECURITY (SIRF APKI ID COMMANDS CHALA SAKTI HAI)
TARGET_USER_ID = 1529085822551326862

# 💳 PAYMENT DETAILS
UPI_ID = '9818940367@fam'
UPI_NAME = 'Krishna'
UPI_QR_URL = 'https://cdn.discordapp.com/attachments/1548769995582869554/1550484011082850384/Screenshot_20260809-233235_FamApp.jpg'

BINANCE_ID = '123456789'
BINANCE_NAME = 'Rathore X Crypto'
BINANCE_QR_URL = 'https://your-image-url.com/binance_qr.png'

# 🖼️ BANNERS
BANNER_IMAGE_URL = 'https://cdn.discordapp.com/attachments/1529086631536234637/1548913864811479070/WLCM.gif'
PURCHASE_BANNER_URL = 'https://media.discordapp.net/attachments/1548769995582869554/1550471469119574067/standard.gif'
SUPPORT_BANNER_URL = 'https://cdn.discordapp.com/attachments/1529086631536234637/1548903192644026489/standard_2.gif'
PAYMENT_BANNER_URL = 'https://media.discordapp.net/attachments/1548769995582869554/1550488423511629914/standard_1.gif'

# 🎫 TICKET CATEGORIES
PURCHASE_CATEGORY_NAME = '🎫┃𝘗𝘜𝘙𝘊𝘏𝘈𝘚𝘌-𝘏𝘌𝘙𝘌'
SUPPORT_CATEGORY_NAME = '🎟️┃𝘚𝘜𝘗𝘗𝘖𝘙𝘛'
PAYMENT_CATEGORY_NAME = '💳┃𝘗𝘈𝘠𝘔𝘌𝘕𝘛-𝘔𝘌𝘛𝘏𝘖𝘋'

# ================= ANTI-NUKE CONFIGURATION =================
ANTI_NUKE_LIMITS = {
    'channel_delete': 3,  # Max channels deleted per 1 min
    'category_delete': 1,  # Max categories deleted per 1 min (Strict punishment)
    'role_delete': 3,  # Max roles deleted per 1 min
    'ban_member': 3,  # Max bans per 1 min
    'kick_member': 3,  # Max kicks per 1 min
}

# Tracking dicts for action counts
action_tracker = defaultdict(lambda: defaultdict(list))


def check_anti_nuke(user_id, action_type):
    if user_id == TARGET_USER_ID:
        return False

    now = datetime.datetime.now(datetime.timezone.utc)
    cutoff = now - datetime.timedelta(seconds=60)

    action_tracker[user_id][action_type] = [
        t for t in action_tracker[user_id][action_type] if t > cutoff
    ]

    action_tracker[user_id][action_type].append(now)

    if (
        len(action_tracker[user_id][action_type])
        >= ANTI_NUKE_LIMITS[action_type]
    ):
        return True
    return False


async def nuke_punish(guild, user, action_name):
    try:
        await guild.ban(
            user, reason=f'[ANTI-NUKE] Triggered mass {action_name}'
        )
        log_channel = guild.get_channel(MOD_LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title='🛡️ ANTI-NUKE TRIGGERED',
                description=f'🚨 **{user.mention}** (`{user.id}`) was BANNED for attempting {action_name}!',
                color=discord.Color.dark_red(),
                timestamp=discord.utils.utcnow(),
            )
            await log_channel.send(embed=embed)
    except Exception as e:
        print(f'Anti-nuke punishment error: {e}')


# ================= GLOBAL OWNER-ONLY CHECK =================
@bot.check
async def restrict_all_commands_to_owner(ctx):
    if ctx.author.id == TARGET_USER_ID:
        return True
    await ctx.send(
        f'❌ {ctx.author.mention}, aap is bot ki commands use nahi kar sakte! Yeh sirf Bot Owner ke liye hai.',
        delete_after=5,
    )
    return False


# ================= CLOSE TICKET BUTTON & TRANSCRIPT =================
class CloseButton(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label='Close Ticket',
        style=discord.ButtonStyle.red,
        emoji='🔒',
        custom_id='close_ticket_button',
    )
    async def close_ticket(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message(
            '🔒 Closing ticket and sending transcript to closed logs...',
            ephemeral=False,
        )

        channel = interaction.channel
        guild = interaction.guild

        messages = []
        async for msg in channel.history(limit=500, oldest_first=True):
            time_str = msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
            messages.append(
                f'[{time_str}] {msg.author} ({msg.author.id}): {msg.clean_content}'
            )

        transcript_text = '\n'.join(messages)
        file_bytes = transcript_text.encode('utf-8')
        transcript_file = discord.File(
            io.BytesIO(file_bytes), filename=f'transcript-{channel.name}.txt'
        )

        closed_log_channel = guild.get_channel(TICKET_CLOSED_CHANNEL_ID)
        if closed_log_channel:
            embed = discord.Embed(
                title='🔒 Ticket Closed',
                description=f'Ticket **#{channel.name}** was closed by {interaction.user.mention}.',
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow(),
            )
            embed.add_field(
                name='👤 Closed By',
                value=f'{interaction.user.mention} (`{interaction.user.id}`)',
                inline=True,
            )
            embed.add_field(
                name='📂 Ticket Name', value=channel.name, inline=True
            )
            await closed_log_channel.send(embed=embed, file=transcript_file)
        else:
            print(
                f'❌ Closed log channel not found! Check ID: {TICKET_CLOSED_CHANNEL_ID}'
            )

        await asyncio.sleep(3)
        await channel.delete()


# ================= TICKET VIEWS & DROPDOWNS =================


class PurchaseDropdown(discord.ui.Select):

    def __init__(self):
        options = [
            discord.SelectOption(
                label='Buy Cheat / Service',
                description='Open ticket to buy cheats or products',
                emoji='🛒',
            ),
            discord.SelectOption(
                label='Inquire Price / Support',
                description='Ask details about pricing',
                emoji='💵',
            ),
        ]
        super().__init__(
            placeholder='Select a purchase option',
            min_values=1,
            max_values=1,
            options=options,
            custom_id='purchase_dropdown_menu',
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
            name=f'purchase-{interaction.user.name.lower()}',
            overwrites=overwrites,
            category=category,
        )

        await interaction.response.send_message(
            f'✅ Ticket created: {ticket_channel.mention}', ephemeral=True
        )

        embed = discord.Embed(
            title='🎫 Purchase Ticket Opened',
            description=f'Welcome {interaction.user.mention}!\nSelected Option: **{selected_option}**\n\nPlease describe what you want to buy. Our staff will respond shortly.',
            color=discord.Color.blue(),
        )
        await ticket_channel.send(
            content=f'{interaction.user.mention}',
            embed=embed,
            view=CloseButton(),
        )

        log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title='🎟️ New Purchase Ticket Opened',
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow(),
            )
            log_embed.add_field(
                name='👤 Opened By',
                value=f'{interaction.user.mention} (`{interaction.user.id}`)',
                inline=False,
            )
            log_embed.add_field(
                name='🏷️ Option Selected', value=selected_option, inline=True
            )
            log_embed.add_field(
                name='📂 Ticket Channel',
                value=ticket_channel.mention,
                inline=True,
            )
            await log_channel.send(
                content=f'<@{TARGET_USER_ID}>', embed=log_embed
            )


class PurchaseView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PurchaseDropdown())


class PaymentDropdown(discord.ui.Select):

    def __init__(self):
        options = [
            discord.SelectOption(
                label='Indian Payment (UPI / QR)',
                description='Pay via PhonePe, Paytm, GPay, UPI QR',
                emoji='🇮🇳',
            ),
            discord.SelectOption(
                label='Binance / Crypto Payment',
                description='Pay via Binance Pay, USDT, Crypto',
                emoji='🟡',
            ),
        ]
        super().__init__(
            placeholder='Select your preferred Payment Method',
            min_values=1,
            max_values=1,
            options=options,
            custom_id='payment_dropdown_menu',
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        member = interaction.user
        selected_option = self.values[0]

        prefix = 'upi' if 'Indian Payment' in selected_option else 'crypto'

        category = discord.utils.get(
            guild.categories, name=PAYMENT_CATEGORY_NAME
        )
        if not category:
            category = await guild.create_category(PAYMENT_CATEGORY_NAME)

        channel_name = f'{prefix}-{member.name.lower()}'
        existing_channel = discord.utils.get(
            guild.channels, name=channel_name
        )

        if existing_channel:
            await interaction.followup.send(
                f'❌ Aapka payment ticket pehle se khula hai: {existing_channel.mention}',
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
            title=f'💳 Payment Ticket: {selected_option}',
            description=f'Hello {member.mention}, welcome!\n\nStaff will send payment details shortly. You can also use `!upi` or `!binance` command here.',
            color=discord.Color.gold(),
        )

        await ticket_channel.send(
            content=f'{member.mention}', embed=embed, view=CloseButton()
        )
        await interaction.followup.send(
            f'✅ Aapka payment ticket ban gaya hai: {ticket_channel.mention}',
            ephemeral=True,
        )

        log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title='💳 New Payment Ticket Opened',
                color=discord.Color.gold(),
                timestamp=discord.utils.utcnow(),
            )
            log_embed.add_field(
                name='👤 Opened By',
                value=f'{member.mention} (`{member.id}`)',
                inline=False,
            )
            log_embed.add_field(
                name='🏷️ Method Selected', value=selected_option, inline=True
            )
            log_embed.add_field(
                name='📂 Ticket Channel',
                value=ticket_channel.mention,
                inline=True,
            )
            await log_channel.send(
                content=f'<@{TARGET_USER_ID}>', embed=log_embed
            )


class PaymentView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PaymentDropdown())


class SupportDropdown(discord.ui.Select):

    def __init__(self):
        options = [
            discord.SelectOption(
                label='General Support',
                description='Get general help from staff team',
                emoji='❓',
            ),
            discord.SelectOption(
                label='Technical Issue',
                description='Get help with errors or issues',
                emoji='⚙️',
            ),
            discord.SelectOption(
                label='Report Player/Issue',
                description='Report a member or server issue',
                emoji='🚨',
            ),
        ]
        super().__init__(
            placeholder='Select a support option',
            min_values=1,
            max_values=1,
            options=options,
            custom_id='support_dropdown_menu',
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

        channel_name = f'support-{member.name.lower()}'
        existing_channel = discord.utils.get(
            guild.channels, name=channel_name
        )

        if existing_channel:
            await interaction.followup.send(
                f'❌ Aapka support ticket pehle se khula hai: {existing_channel.mention}',
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
            title=f'🛠️ Support Ticket: {selected_option}',
            description=f'Hello {member.mention}, welcome to Support! Please explain your issue, and our staff team will assist you shortly.',
            color=discord.Color.from_rgb(57, 255, 20),
        )

        await ticket_channel.send(
            content=f'{member.mention}', embed=embed, view=CloseButton()
        )
        await interaction.followup.send(
            f'✅ Aapka support ticket ban gaya hai: {ticket_channel.mention}',
            ephemeral=True,
        )

        log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title='🛠️ New Support Ticket Opened',
                color=discord.Color.from_rgb(57, 255, 20),
                timestamp=discord.utils.utcnow(),
            )
            log_embed.add_field(
                name='👤 Opened By',
                value=f'{member.mention} (`{member.id}`)',
                inline=False,
            )
            log_embed.add_field(
                name='🏷️ Issue Type', value=selected_option, inline=True
            )
            log_embed.add_field(
                name='📂 Ticket Channel',
                value=ticket_channel.mention,
                inline=True,
            )
            await log_channel.send(
                content=f'<@{TARGET_USER_ID}>', embed=log_embed
            )


class SupportView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SupportDropdown())


# ================= BOT EVENTS =================
@bot.event
async def on_ready():
    bot.add_view(PurchaseView())
    bot.add_view(PaymentView())
    bot.add_view(SupportView())
    bot.add_view(CloseButton())
    print(f'🛡️ {bot.user} Rathore X Cheats Bot Online Hai!')


@bot.event
async def on_member_join(member):
    if member.bot:
        try:
            async for entry in member.guild.audit_logs(
                limit=1, action=discord.AuditLogAction.bot_add
            ):
                if entry.user.id != TARGET_USER_ID:
                    await member.ban(
                        reason='[ANTI-BOT] Unauthorised bot added'
                    )
                    await member.guild.ban(
                        entry.user, reason='[ANTI-BOT] Added unauthorized bot'
                    )
                    return
        except Exception as e:
            print(f'Anti-Bot Error: {e}')

    role = discord.utils.get(member.guild.roles, name=AUTO_ROLE_NAME)
    if role:
        try:
            await member.add_roles(role)
        except Exception as e:
            print(f'Role error: {e}')

    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        content_text = f'{member.mention} Welcome to **RATHORE COMMUNITY**!!!'
        embed_description = (
            '📌 | **<#1548747102799269959>**\n'
            'MAKE SURE YOU READ ALL THE RULES\n\n'
            '📢 | **<#1548747535147860098>**\n'
            'ALL THE ANNOUNCEMENT ARE THERE\n\n'
            '💬 | **<#1548759359402676244>**\n'
            'INTRODUCE YOURSELF HERE BY CHATTING IN GENERAL CHAT\n\n'
            'YOU HAVE A GOOD DAY IN **RATHORE COMMUNITY** !! AND THANKS FOR A'
            ' PART OF OUR COMMUNITY'
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
            title='📥 Member Joined',
            description=f'{member.mention} ({member.name}) ne server join kiya!',
            color=discord.Color.green(),
        )
        log_embed.set_thumbnail(url=member.display_avatar.url)
        await log_channel.send(embed=log_embed)


@bot.event
async def on_member_remove(member):
    log_channel = bot.get_channel(JOIN_LEAVE_CHANNEL_ID)
    if log_channel:
        log_embed = discord.Embed(
            title='📤 Member Left',
            description=f'**{member.name}** ne server chor diya hai.',
            color=discord.Color.red(),
        )
        log_embed.set_thumbnail(url=member.display_avatar.url)
        await log_channel.send(embed=log_embed)


# ================= AUDIT LOG & ANTI-NUKE LISTENERS =================


# 1. ANTI-NUKE: CHANNEL & CATEGORY DELETE PROTECTION
@bot.event
async def on_guild_channel_delete(channel):
    try:
        async for entry in channel.guild.audit_logs(
            limit=1, action=discord.AuditLogAction.channel_delete
        ):
            executor = entry.user

            # Category Delete Detection
            if isinstance(channel, discord.CategoryChannel):
                if check_anti_nuke(executor.id, 'category_delete'):
                    await nuke_punish(channel.guild, executor, 'Category Delete')
            # Text / Voice Channel Delete Detection
            else:
                if check_anti_nuke(executor.id, 'channel_delete'):
                    await nuke_punish(channel.guild, executor, 'Channel Delete')
            break
    except Exception as e:
        print(f'Anti-Nuke Channel/Category Delete Error: {e}')


# 2. ANTI-NUKE: ROLE DELETE PROTECTION
@bot.event
async def on_guild_role_delete(role):
    try:
        async for entry in role.guild.audit_logs(
            limit=1, action=discord.AuditLogAction.role_delete
        ):
            executor = entry.user
            if check_anti_nuke(executor.id, 'role_delete'):
                await nuke_punish(role.guild, executor, 'Role Delete')
            break
    except Exception as e:
        print(f'Anti-Nuke Role Delete Error: {e}')


# 3. ANTI-NUKE: BAN AUDIT MONITORING
@bot.event
async def on_member_ban(guild, user):
    try:
        async for entry in guild.audit_logs(
            limit=1, action=discord.AuditLogAction.ban
        ):
            executor = entry.user
            if executor.id != bot.user.id and check_anti_nuke(
                executor.id, 'ban_member'
            ):
                await nuke_punish(guild, executor, 'Member Ban')
            break
    except Exception as e:
        print(f'Anti-Nuke Ban Error: {e}')


# 4. MESSAGE DELETE LOG
@bot.event
async def on_message_delete(message):
    if message.author and message.author.bot:
        return

    cached_data = MESSAGE_CACHE.get(message.id, None)
    author = message.author or (
        cached_data.get('author') if cached_data else None
    )
    content = message.content or (
        cached_data.get('content') if cached_data else None
    )
    channel = message.channel

    log_channel = bot.get_channel(AUDIT_LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(
            title='🗑️ Message Deleted',
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow(),
        )

        author_str = (
            f'{author.mention} (`{author.id}`)' if author else 'Unknown User'
        )
        content_str = (
            content if content else '*[Image/Attachment/Uncached Content]*'
        )

        embed.add_field(name='Author', value=author_str, inline=True)
        embed.add_field(
            name='Channel',
            value=channel.mention if channel else 'Unknown',
            inline=True,
        )
        embed.add_field(
            name='Deleted Content', value=content_str, inline=False
        )
        embed.set_footer(text=f'Message ID: {message.id}')

        await log_channel.send(embed=embed)

    if message.id in MESSAGE_CACHE:
        del MESSAGE_CACHE[message.id]


# 5. ROLE CREATE LOG
@bot.event
async def on_guild_role_create(role):
    log_channel = bot.get_channel(AUDIT_LOG_CHANNEL_ID)
    if not log_channel:
        return

    creator_str = 'Unknown User'
    try:
        await asyncio.sleep(1)
        async for entry in role.guild.audit_logs(
            limit=1, action=discord.AuditLogAction.role_create
        ):
            if entry.target.id == role.id:
                creator_str = f'{entry.user.mention} (`{entry.user.id}`)'
                break
    except Exception as e:
        print(f'Audit Log Error: {e}')

    embed = discord.Embed(
        title='🛠️ New Role Created',
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow(),
    )
    embed.add_field(
        name='Role Name', value=f'{role.mention} (`{role.name}`)', inline=True
    )
    embed.add_field(name='Role ID', value=f'`{role.id}`', inline=True)
    embed.add_field(name='Created By', value=creator_str, inline=False)
    embed.set_footer(text=f'Server: {role.guild.name}')

    await log_channel.send(embed=embed)


# 6. MESSAGE EDIT LOG
@bot.event
async def on_message_edit(before, after):
    if before.author and before.author.bot:
        return
    if before.content == after.content:
        return

    MESSAGE_CACHE[after.id] = {
        'author': after.author,
        'content': after.content,
    }

    log_channel = bot.get_channel(AUDIT_LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(
            title='✏️ Message Edited',
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow(),
        )
        author_str = (
            f'{before.author.mention} (`{before.author.id}`)'
            if before.author
            else 'Unknown User'
        )
        embed.add_field(name='Author', value=author_str, inline=True)
        embed.add_field(
            name='Channel',
            value=before.channel.mention if before.channel else 'Unknown',
            inline=True,
        )
        embed.add_field(
            name='Before',
            value=before.content if before.content else '*Empty*',
            inline=False,
        )
        embed.add_field(
            name='After',
            value=after.content if after.content else '*Empty*',
            inline=False,
        )
        embed.set_footer(text=f'Message ID: {before.id}')
        await log_channel.send(embed=embed)


# --- AUTOMOD & COMMAND PROCESSOR ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    MESSAGE_CACHE[message.id] = {
        'author': message.author,
        'content': message.content,
    }

    msg_content = message.content.lower()

    # 1. Invite Link Check
    discord_invite_pattern = r'(discord\.gg|discord\.com/invite)/[a-zA-Z0-9]+'
    if re.search(discord_invite_pattern, msg_content):
        try:
            await message.delete()
            await message.channel.send(
                f'⚠️ {message.author.mention}, invite links allowed nahi hain!',
                delete_after=5,
            )
        except Exception as e:
            print(f'Delete Error: {e}')
        return

    # 2. Owner Mention Check
    user_tagged = any(user.id == TARGET_USER_ID for user in message.mentions)
    if user_tagged or message.mention_everyone:
        try:
            await message.delete()
            await message.channel.send(
                f'⚠️ {message.author.mention}, owner ko ping nahi kar sakte!',
                delete_after=5,
            )
        except Exception as e:
            print(f'Delete Error: {e}')
        return

    # 3. Bad Words Check
    for word in BAD_WORDS:
        if word in msg_content:
            try:
                await message.delete()
                await message.channel.send(
                    f'⚠️ {message.author.mention}, bad words allowed nahi hain!',
                    delete_after=5,
                )
            except Exception as e:
                print(f'Delete Error: {e}')
            return

    await bot.process_commands(message)


# ================= COMMANDS =================


@bot.command()
async def purchasepanel(ctx):
    await ctx.message.delete()
    description_text = (
        'Welcome to **RATHORE X CHEATS**, your trusted source for premium'
        ' modifications, tools, and exclusive services. Create a ticket below'
        ' to receive fast support, purchase assistance, or answers to your'
        ' questions.\n\n📌 **RULES**\n• Create tickets only for purchases,'
        ' support, or legitimate inquiries.\n• Creating tickets for fun,'
        ' trolling, or wasting staff time will result in a ban.\n• All prices'
        ' are listed publicly. Do not create tickets to negotiate or'
        ' bargain.\n• Be respectful to staff members at all times.\n• Do not'
        ' spam, ping staff repeatedly, or create multiple tickets for the'
        ' same issue.\n• Payments must be completed through approved methods'
        ' only.\n\n🔥 **Why Choose RATHORE X CHEATS !!**\n✓ Fast Support\n✓'
        ' Secure Transactions\n✓ Premium Quality Services\n✓ Trusted'
        ' Community\n✓ Professional Assistance\n\nClick the button below to'
        ' create a ticket and get started.\n\n👑 **RATHORE X CHEATS @2026 | by'
        ' RATHORE !! |**'
    )
    embed = discord.Embed(
        description=description_text,
        color=discord.Color.from_rgb(88, 101, 242),
    )
    embed.set_footer(text='Powered by Owner 1nonlyrathore8')
    if PURCHASE_BANNER_URL:
        embed.set_image(url=PURCHASE_BANNER_URL)
    await ctx.send(embed=embed, view=PurchaseView())


@bot.command()
async def paymentpanel(ctx):
    await ctx.message.delete()
    description_text = (
        '💳 **RATHORE X — PAYMENT METHODS**\n\n🔐 **SELECT YOUR PREFERRED'
        ' PAYMENT METHOD**\nChoose any available payment option below to'
        ' receive the complete payment details.\n\n🇮🇳 **INDIAN PAYMENT'
        ' METHODS**\n• 📱 PhonePe / Paytm / Google Pay / UPI QR\n\n🟡 **CRYPTO'
        ' PAYMENT METHODS**\n• 🟡 Binance Pay / USDT (TRC20/BEP20)\n\n📌'
        ' **PAYMENT INSTRUCTIONS**\n1. Select your preferred payment method.\n2.'
        ' Complete payment & send clear screenshot + Transaction ID.\n3. Wait'
        ' for confirmation from staff.\n\n👑 **POWERED BY RATHORE !!**'
    )
    embed = discord.Embed(
        description=description_text, color=discord.Color.gold()
    )
    embed.set_footer(text='Powered by Owner 1nonlyrathore8')
    if PAYMENT_BANNER_URL:
        embed.set_image(url=PAYMENT_BANNER_URL)
    await ctx.send(embed=embed, view=PaymentView())


@bot.command()
async def supportpanel(ctx):
    await ctx.message.delete()
    description_text = (
        '🛠️ **RATHORE X CHEATS — SUPPORT TICKET**\n\nNeed help? Our support'
        ' team is here to assist you with technical issues, account problems,'
        ' or product questions.\n\n📌 **SUPPORT RULES**\n• Open tickets only'
        ' for genuine support requests.\n• Clearly explain your issue with'
        ' screenshots.\n• Be respectful and patient while waiting for'
        ' staff.\n\n👑 **RATHORE X CHEATS @2026 | by RATHORE !! |**'
    )
    embed = discord.Embed(
        description=description_text, color=discord.Color.from_rgb(57, 255, 20)
    )
    embed.set_footer(text='Powered by Owner 1nonlyrathore8')
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
        title='💳 Indian Payment Details (UPI / QR)',
        description=(
            'Send payment to details below and share **screenshot +'
            ' Transaction ID**:\n\n'
            f'🔹 **UPI ID:** `{UPI_ID}`\n'
            f'🔹 **Payee Name:** {UPI_NAME}\n\n'
            '⚠️ *Payment complete hone ke baad screenshot zaroor bhejein!*'
        ),
        color=discord.Color.green(),
    )
    if UPI_QR_URL:
        embed.set_image(url=UPI_QR_URL)
    embed.set_footer(text='Rathore X Cheats | Secure Payment System')
    await ctx.send(embed=embed)


@bot.command()
async def binance(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass
    embed = discord.Embed(
        title='🟡 Binance / Crypto Payment Details',
        description=(
            'Send payment using Binance Pay ID or Crypto address:\n\n'
            f'🔹 **Binance Pay ID / Address:** `{BINANCE_ID}`\n'
            f'🔹 **Account Name:** {BINANCE_NAME}\n\n'
            '⚠️ *Double check the address before sending crypto!*'
        ),
        color=discord.Color.gold(),
    )
    if (
        BINANCE_QR_URL
        and BINANCE_QR_URL != 'https://your-image-url.com/binance_qr.png'
    ):
        embed.set_image(url=BINANCE_QR_URL)
    embed.set_footer(text='Rathore X Cheats | Crypto Payment System')
    await ctx.send(embed=embed)


@bot.command()
async def lock(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass
    role = discord.utils.get(ctx.guild.roles, name=AUTO_ROLE_NAME)
    if role is None:
        await ctx.send(f'❌ Role `{AUTO_ROLE_NAME}` nahi mila!', delete_after=5)
        return
    try:
        await ctx.channel.set_permissions(role, send_messages=False)
        await ctx.send(
            f'🔒 **{role.name}** role ke liye yeh channel lock kar diya gaya'
            ' hai!'
        )
    except Exception as e:
        await ctx.send(f'❌ Error: {e}', delete_after=5)


@bot.command()
async def unlock(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass
    role = discord.utils.get(ctx.guild.roles, name=AUTO_ROLE_NAME)
    if role is None:
        await ctx.send(f'❌ Role `{AUTO_ROLE_NAME}` nahi mila!', delete_after=5)
        return
    try:
        await ctx.channel.set_permissions(role, send_messages=True)
        await ctx.send(
            f'🔓 **{role.name}** role ke liye yeh channel unlock kar diya gaya'
            ' hai!'
        )
    except Exception as e:
        await ctx.send(f'❌ Error: {e}', delete_after=5)


@bot.command()
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'🧹 {amount} messages delete kar diye gaye!', delete_after=3)


@bot.command()
async def kick(ctx, member: discord.Member, *, reason='Koyi reason nahi diya'):
    if check_anti_nuke(ctx.author.id, 'kick_member'):
        await nuke_punish(ctx.guild, ctx.author, 'Kick')
        return

    await member.kick(reason=reason)
    await ctx.send(
        f'🚨 {member.mention} ko kick kar diya gaya. Reason: {reason}'
    )

    mod_channel = bot.get_channel(MOD_LOG_CHANNEL_ID)
    if mod_channel:
        embed = discord.Embed(
            title='👢 Member Kicked', color=discord.Color.orange()
        )
        embed.add_field(
            name='User', value=f'{member.mention} ({member.name})', inline=True
        )
        embed.add_field(
            name='Moderator', value=ctx.author.mention, inline=True
        )
        embed.add_field(name='Reason', value=reason, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        await mod_channel.send(embed=embed)


@bot.command()
async def ban(ctx, member: discord.Member, *, reason='Rule break kiya'):
    if check_anti_nuke(ctx.author.id, 'ban_member'):
        await nuke_punish(ctx.guild, ctx.author, 'Ban')
        return

    await member.ban(reason=reason)
    await ctx.send(f'⛔ {member.mention} ko BAN kar diya gaya. Reason: {reason}')

    mod_channel = bot.get_channel(MOD_LOG_CHANNEL_ID)
    if mod_channel:
        embed = discord.Embed(
            title='🔨 Member Banned', color=discord.Color.dark_red()
        )
        embed.add_field(
            name='User', value=f'{member.mention} ({member.name})', inline=True
        )
        embed.add_field(
            name='Moderator', value=ctx.author.mention, inline=True
        )
        embed.add_field(name='Reason', value=reason, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        await mod_channel.send(embed=embed)


@bot.command()
async def timeout(
    ctx,
    member: discord.Member,
    minutes: int = 10,
    *,
    reason='Rule break kiya',
):
    if member == ctx.author:
        await ctx.send('❌ Aap khud ko timeout nahi de sakte!')
        return

    if member.top_role >= ctx.guild.me.top_role:
        await ctx.send(
            '❌ Main is user ko timeout nahi de sakta kyunki iska Role mere Bot'
            ' Role se bada ya barabar hai!'
        )
        return

    duration = datetime.timedelta(minutes=minutes)
    try:
        await member.timeout(duration, reason=reason)
        await ctx.send(
            f'⏳ {member.mention} ko **{minutes} minute** ke liye timeout kar'
            ' diya gaya.'
        )

        mod_channel = bot.get_channel(MOD_LOG_CHANNEL_ID)
        if mod_channel:
            embed = discord.Embed(
                title='⏳ Member Timed Out', color=discord.Color.gold()
            )
            embed.add_field(
                name='User',
                value=f'{member.mention} ({member.name})',
                inline=True,
            )
            embed.add_field(
                name='Duration', value=f'{minutes} Minutes', inline=True
            )
            embed.add_field(
                name='Moderator', value=ctx.author.mention, inline=True
            )
            embed.add_field(name='Reason', value=reason, inline=False)
            embed.set_thumbnail(url=member.display_avatar.url)
            await mod_channel.send(embed=embed)

    except discord.Forbidden:
        await ctx.send(
            '❌ **Forbidden Error:** Mere paas `Moderate Members` permission'
            ' nahi hai ya yeh user Admin hai.'
        )
    except Exception as e:
        await ctx.send(f'❌ Error: {e}', delete_after=5)


@bot.command()
async def untimeout(ctx, member: discord.Member):
    try:
        await member.timeout(None)
        await ctx.send(f'✅ {member.mention} ka timeout hata diya gaya hai.')
    except Exception as e:
        await ctx.send(f'❌ Error: {e}', delete_after=5)


@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')


@bot.command()
async def price(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass

    description_text = (
        '<a:259419darkbluearrow:1550842821940879432> **RATHORE X AIMKILL**\n\n'
        '<a:259419darkbluearrow:1550842821940879432> **PANEL FEATURES**\n\n'
        '**AIM FEATURES**\n\n'
        '<a:259419darkbluearrow:1550842821940879432> AIMKILL MAX [ COVER ]\n'
        '<a:259419darkbluearrow:1550842821940879432> AIM ASSIST\n'
        '<a:259419darkbluearrow:1550842821940879432> NO HIT DELAY\n'
        '<a:259419darkbluearrow:1550842821940879432> FOV - 999X\n\n'
        '**VISUAL FEATURES**\n\n'
        '<a:259419darkbluearrow:1550842821940879432> ESP LINE\n'
        '<a:259419darkbluearrow:1550842821940879432> ESP INFO\n'
        '<a:259419darkbluearrow:1550842821940879432> ESP DISTANCE\n'
        '<a:259419darkbluearrow:1550842821940879432> ESP BOX\n'
        '<a:259419darkbluearrow:1550842821940879432> ESP CLOSEST\n'
        '<a:259419darkbluearrow:1550842821940879432> ESP GRENADE\n'
        '<a:259419darkbluearrow:1550842821940879432> ESP NAME\n'
        '<a:259419darkbluearrow:1550842821940879432> TRACKER, ETC.\n\n'
        '**MISC FEATURES**\n\n'
        '<a:259419darkbluearrow:1550842821940879432> DOWNKILL\n'
        '<a:259419darkbluearrow:1550842821940879432> EXECUTER\n'
        '<a:259419darkbluearrow:1550842821940879432> UPWARD DYNEX [ 200X ]\n'
        '<a:259419darkbluearrow:1550842821940879432> TELEPORT PLAYER\n'
        '<a:259419darkbluearrow:1550842821940879432> UPCOMING AUTO TELEPORT\n'
        '<a:259419darkbluearrow:1550842821940879432> UPCOMING JUMP REVISER\n'
        '<a:259419darkbluearrow:1550842821940879432> LOCK POSITION\n'
        '<a:259419darkbluearrow:1550842821940879432> BASE BREAKER\n'
        '<a:259419darkbluearrow:1550842821940879432> GHOST HACK\n'
        '<a:259419darkbluearrow:1550842821940879432> SHAKE KILL\n\n'
        '**GLOBAL FEATURES**\n\n'
        '<a:259419darkbluearrow:1550842821940879432> SPEED JOYSTICK\n'
        '<a:259419darkbluearrow:1550842821940879432> SPEED SCALER\n'
        '<a:259419darkbluearrow:1550842821940879432> NIGHT MODE\n'
        '<a:259419darkbluearrow:1550842821940879432> LOOK & EMOTE CHANGER\n'
        '<a:259419darkbluearrow:1550842821940879432> 11+ PREMIUM LOOK'
        ' CHANGERS\n'
        '<a:259419darkbluearrow:1550842821940879432> 7+ PREMIUM EMOTE'
        ' CHANGERS\n'
        '<a:259419darkbluearrow:1550842821940879432> MORE THAN 40+'
        ' FEATURES\n\n'
        '**SETTING FEATURES**\n\n'
        '<a:259419darkbluearrow:1550842821940879432> RESET GUEST\n'
        '<a:259419darkbluearrow:1550842821940879432> KEYBIND SUPPORT\n'
        '<a:259419darkbluearrow:1550842821940879432> TOPMOST SUPPORT\n'
        '<a:259419darkbluearrow:1550842821940879432> THEME SUPPORT\n'
        '<a:259419darkbluearrow:1550842821940879432> MORE THAN 40+'
        ' FEATURES\n\n'
        '**PRICES :**\n\n'
        '<a:259419darkbluearrow:1550842821940879432> **1 DAYS - 140 INR | 1.60'
        ' USD**\n'
        '<a:259419darkbluearrow:1550842821940879432> **7 DAYS - 600 INR | 7'
        ' USD**\n'
        '<a:259419darkbluearrow:1550842821940879432> **30 DAYS - 1800 INR | 20'
        ' USD**\n'
        '<a:259419darkbluearrow:1550842821940879432> **LIFETIME - 4500 INR | 40'
        ' USD**\n\n'
        '**FOR PURCHASE** <#1550562248932724756>'
    )

    embed = discord.Embed(
        description=description_text,
        color=discord.Color.from_rgb(0, 162, 255),
    )

    banner_url = 'https://media.discordapp.net/attachments/1529086631536234637/1530160532974211283/standard_1.gif'
    embed.set_image(url=banner_url)

    await ctx.send(embed=embed)


@bot.command()
async def silentkill(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass

    e = '<a:259419darkbluearrow:1550842821940879432>\u3000'

    description_text = (
        f'{e}**RATHORE X SILENT KILL**\n\n'
        f'{e}**PANEL FUNCTIONS**\n\n'
        '**AIMBOT MODULE**\n\n'
        f'{e}ENABLE ALL\n'
        f'{e}SILENT AIM\n'
        f'{e}PULL 360\n'
        f'{e}SHOW BEHIND ENEMY\n'
        f'{e}FLY HACK\n'
        f'{e}TELEPORT\n'
        f'{e}GHOST\n'
        f'{e}JOYSTICK SPEED\n'
        f'{e}SPEED RUN\n\n'
        '**VISUALS MODULE**\n\n'
        f'{e}ESP LINE\n'
        f'{e}ESP BOX\n'
        f'{e}ESP NAME\n'
        f'{e}ESP HEALTH\n'
        f'{e}ESP DISTANCE\n\n'
        '**CORE USP :**\n\n'
        f'{e}REGULAR UPDATES\n'
        f'{e}FASTEST SUPPORT\n'
        f'{e}ALL SERVER SAFE\n\n'
        '**SETTINGS**\n\n'
        f'{e}RESET GUEST\n\n'
        '**PRICES**\n\n'
        f'{e}**7 DAYS - 650 INR**\n'
        f'{e}**14 DAYS - 1000 INR**\n'
        f'{e}**30 DAYS - 1850 INR**\n\n'
        '**FOR PURCHASE** <#1550562248932724756>'
    )

    embed = discord.Embed(
        description=description_text,
        color=discord.Color.from_rgb(0, 162, 255),
    )

    banner_url = 'https://media.discordapp.net/attachments/1529086631536234637/1530162682630766713/standard_2.gif?ex=6aafb80c&is=6aae668c&hm=6a000d56a052d47af2d56ef4205d37be309fc40bd3ed294aea9d7abcfb9c389e&=&width=512&height=180'
    embed.set_image(url=banner_url)

    await ctx.send(embed=embed)


@bot.command()
async def emulatorbypass(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass

    e = '<a:259419darkbluearrow:1550842821940879432>\u3000'

    description_text = (
        f'{e}**RATHORE X BYPASS**\n'
        f'{e}**EMULATOR BYPASS (LIB-BASED) – NEW BR SEASON**\n\n'
        f'{e}**PLAY THE NEW BR SEASON WITHOUT RESTRICTIONS**\n\n'
        '**FEATURES**\n\n'
        f'{e}NO UID RESTRICTION\n'
        f'{e}PLAY ON UNLIMITED IDS\n'
        f'{e}SAFE FOR MAIN ACCOUNT\n'
        f'{e}NO LIMIT ON KILLS\n\n'
        '**PRICING**\n\n'
        f'{e}**1 DAY – ₹120**\n'
        f'{e}**7 DAYS – ₹500**\n'
        f'{e}**15 DAYS – ₹800**\n'
        f'{e}**1 MONTH – ₹1500**\n'
        f'{e}**PERMANENT – ₹4500**\n\n'
        '**FOR PURCHASE** <#1550562248932724756>'
    )

    embed = discord.Embed(
        description=description_text,
        color=discord.Color.from_rgb(0, 162, 255),
    )

    banner_url = 'https://media.discordapp.net/attachments/1490095245302431868/1518999070457200752/standard.gif?ex=6aaf50e0&is=6aadff60&hm=8181c16843246bf0ffb50c20d1287345ecd9640de6680179147a858c8d95ce8a&='
    embed.set_image(url=banner_url)

    await ctx.send(embed=embed)


@bot.command()
async def paidpush(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass

    e = '<a:259419darkbluearrow:1550842821940879432>\u3000'

    description_text = (
        f'{e}**RATHORE X PAID PUSH**\n\n'
        f'{e}**PAID PUSH PRICING**\n\n'
        f'{e}**20 STAR = 80 INR**\n'
        f'{e}**40 STAR = 160 INR**\n'
        f'{e}**60 STAR = 240 INR**\n'
        f'{e}**80 STAR = 320 INR**\n'
        f'{e}**100 STAR = 400 INR**\n'
        f'{e}**200 STAR = 800 INR**\n'
        f'{e}**300 STAR = 1200 INR**\n'
        f'{e}**400 STAR = 1600 INR**\n'
        f'{e}**500 STAR = 2000 INR**\n'
        f'{e}**999 STAR = 2999 INR**\n\n'
        '**FOR PURCHASE** <#1550562248932724756>'
    )

    embed = discord.Embed(
        description=description_text,
        color=discord.Color.from_rgb(0, 162, 255),
    )

    banner_url = 'https://media.discordapp.net/attachments/1490095245302431868/1519005559347478818/standard_2.gif?ex=6aaf56eb&is=6aae056b&hm=241c3c051ae74c731f460040df41c73d236d800cd077cce8387690ee7d9aa01c&'
    embed.set_image(url=banner_url)

    await ctx.send(embed=embed)


@bot.command()
async def level8ids(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass

    e = '<a:259419darkbluearrow:1550842821940879432>\u3000'

    description_text = (
        f'{e}**LV 8 IDS**\n\n'
        f'{e}**STOCK = UNLIMITED**\n\n'
        f'{e}**PRICE: 5 ID IN JUST 100 INR**\n\n'
        '**FOR PURCHASE** <#1550562248932724756>'
    )

    embed = discord.Embed(
        description=description_text,
        color=discord.Color.from_rgb(0, 162, 255),
    )

    banner_url = 'https://media.discordapp.net/attachments/1490095245302431868/1519001574742036761/standard_1.gif?ex=6aaf5335&is=6aae01b5&hm=93a8da68d2d2238bd90cf9bc0c98af2dd89eb8f02c177b8bd8f094d9b4132b98&='
    embed.set_image(url=banner_url)

    await ctx.send(embed=embed)


@bot.command()
async def rules(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass

    e = '<a:259419darkbluearrow:1550842821940879432>\u3000'

    description_text = (
        f'{e}**RATHORE X RULES**\n\n'
        f'{e}**WELCOME TO RATHORE SERVER !!**\n\n'
        '**BE RESPECTFUL :**\n'
        f'{e}TREAT EVERYONE WITH RESPECT. NO TOXIC BEHAVIOR, HATE SPEECH, PERSONAL'
        ' ATTACKS, IMPERSONATION, FALSE ACCUSATIONS, OR ANY DISRESPECTFUL'
        ' CONDUCT WILL BE TOLERATED.\n\n'
        '**KEEP CHANNELS CLEAN :**\n'
        f'{e}NO SPAMMING, COPYING & PASTING REPEATEDLY, BEGGING, ADVERTISING'
        ' OTHER SERVERS, OR POSTING NSFW/DISTURBING CONTENT. DISCUSSIONS ABOUT'
        ' CHEATS OR ANY ILLEGAL ACTIVITY ARE STRICTLY PROHIBITED.\n\n'
        '**NO PROMOTION :**\n'
        f'{e}PROMOTION OF OTHER SERVERS, PRODUCTS, OR SERVICES WITHOUT'
        ' PERMISSION IS STRICTLY PROHIBITED.\n\n'
        '**USE APPROPRIATE NAMES & PROFILES :**\n'
        f'{e}CHOOSE A CLEAN, NON-OFFENSIVE USERNAME, AVATAR, AND PROFILE.'
        ' INAPPROPRIATE OR OFFENSIVE CONTENT WILL BE REMOVED IMMEDIATELY.\n\n'
        '**NO FILTER OR PUNISHMENT EVASION :**\n'
        f'{e}DO NOT TRY TO BYPASS FILTERS OR PUNISHMENTS. DOING SO WILL LEAD TO'
        ' FURTHER DISCIPLINARY ACTION.\n\n'
        '**SUPPORT POLICY :**\n'
        f'{e}THERE IS NO SUPPORT FOR FREE IMGUI VERSIONS. IF YOU HAVE PURCHASED'
        ' A PRODUCT, YOU GET 3 DAYS OF FREE SUPPORT ONLY. DMING STAFF DIRECTLY'
        ' WILL LEAD TO TIMEOUTS OR PERMANENT BANS.\n\n'
        '**STAY INFORMED :**\n'
        f'{e}PLEASE READ ALL CHANNELS CAREFULLY, INCLUDING OUR TERMS OF'
        ' SERVICE, REFUND POLICY, AND PRIVACY POLICY, AVAILABLE ON THE WEBSITE'
        ' AND SERVER.\n\n'
        '**REFUND POLICY :**\n'
        f'{e}WE STRIVE TO PROVIDE QUALITY SERVICES AND PRODUCTS. REFUNDS ARE'
        ' CONSIDERED ONLY UNDER GENUINE ISSUES AND WITHIN A LIMITED TIMEFRAME.'
        ' PLEASE CONTACT SUPPORT PROMPTLY WITH VALID REASONS. ALL REFUND'
        ' REQUESTS ARE SUBJECT TO REVIEW AND APPROVAL.\n\n'
        f'{e}**BY JOINING RATHORE SERVER , YOU AGREE TO FOLLOW THESE RULES.'
        ' THANK YOU FOR HELPING US BUILD A RESPECTFUL AND TRUSTWORTHY'
        ' COMMUNITY**\n\n'
    )

    embed = discord.Embed(
        description=description_text,
        color=discord.Color.from_rgb(0, 162, 255),
    )

    banner_url = 'https://media.discordapp.net/attachments/1529086631536234637/1548911076505030656/SERVER_RULES.gif?ex=6aaf5eda&is=6aae0d5a&hm=21191945043f4c5293e08011c7f95b141ab0078bacf8a44730b450f859cb6114&'
    embed.set_image(url=banner_url)

    await ctx.send(embed=embed)


# ================= RUN SERVER & BOT =================
if __name__ == '__main__':
    keep_alive()
    token = (
        os.environ.get('DISCORD_TOKEN')
        or os.getenv('TOKEN')
        or os.environ.get('DISCORD_BOT_TOKEN')
    )
    if token:
        bot.run(token)
    else:
        print('❌ Token nahi mila!')
