import discord
from discord.ext import commands, tasks
import asyncio
import random
import json
from datetime import datetime, timezone

# --- Učitaj konfiguraciju ---
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

TOKEN = config["TOKEN"]
PREFIX = config.get("PREFIX", "?")
GUILD_ID = int(config["GUILD_ID"])
WELCOME_CHANNEL_ID = int(config["WELCOME_CHANNEL_ID"])
LEFT_CHANNEL_ID = int(config["LEFT_CHANNEL_ID"])
LOG_CHANNEL_ID = int(config["LOG_CHANNEL_ID"])

# --- Inicijalizacija bota ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=("?", "!"), intents=intents)

# 🎨 Slike za različite evente i funkcije
LINKOVI = {
    "giveaway": {
        "logo": "https://cdn.discordapp.com/attachments/1426634834855592068/1426669188700832015/standard_26.gif?ex=68ec10b8&is=68eabf38&hm=5a96935b8832122e560d3e0cf9ee2e89077084caab61199e2855d8bf84b95384&",
    },
    "welcome": {
        "logo": "https://cdn.discordapp.com/attachments/1426634834855592068/1426669188700832015/standard_26.gif?ex=68ec10b8&is=68eabf38&hm=5a96935b8832122e560d3e0cf9ee2e89077084caab61199e2855d8bf84b95384&",
        "banner": "https://cdn.discordapp.com/attachments/1420503570590994553/1427338152422543431/Dobrodosao_1.gif?ex=68ee7fbe&is=68ed2e3e&hm=fc4f870b15b119744292dd4a16faf61b2a95de8bb59cb5b832fcac7cc37c4674&"
    },
    "left": {
        "logo": "https://cdn.discordapp.com/attachments/1426634834855592068/1426669188700832015/standard_26.gif?ex=68ec10b8&is=68eabf38&hm=5a96935b8832122e560d3e0cf9ee2e89077084caab61199e2855d8bf84b95384&",
        "banner": "https://cdn.discordapp.com/attachments/1420503570590994553/1427338191853195315/Dobrodosao_2.gif?ex=68ee7fc7&is=68ed2e47&hm=a6709e3a61486b0eea2d0c96abefc6768e3912ceb00a5191653d5d652b4f142a&"
    }
}

# -------------------------------
# ON READY
# -------------------------------
@bot.event
async def on_ready():
    print(f"✅ Bot je online kao {bot.user}")
    update_status.start()

# -------------------------------
# STATUS UPDATE
# -------------------------------
@tasks.loop(minutes=1)
async def update_status():
    guild = bot.get_guild(GUILD_ID)
    if guild:
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"({guild.member_count}) ➜ Members"
            )
        )

# -------------------------------
# LEFT EVENT
# -------------------------------
@bot.event
async def on_member_remove(member):
    """Šalje poruku kad korisnik napusti server."""
    channel = bot.get_channel(LEFT_CHANNEL_ID)
    if channel is None:
        print("⚠️ Kanal za left poruke nije pronađen.")
        return

    logo = LINKOVI["left"]["logo"]
    banner = LINKOVI["left"]["banner"]

    embed = discord.Embed(
        title="👋 Član je napustio server",
        description=f"Doviđenja brate, nadamo se da ste uživali u najjačem serveru!! 👋\n\n👤 **{member.name}**",
        color=0x2ecc71
    )
    embed.set_thumbnail(url=logo)
    embed.set_image(url=banner)
    embed.set_footer(text=f"{member.guild.name} • Nadamo se da će se vratiti!", icon_url=logo)
    await channel.send(embed=embed)

# -------------------------------
# WELCOME EVENT
# -------------------------------
@bot.event
async def on_member_join(member):
    """Automatski šalje welcome poruku kada korisnik uđe na server."""
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel is None:
        print("⚠️ Welcome kanal nije pronađen.")
        return

    logo = LINKOVI["welcome"]["logo"]
    banner = LINKOVI["welcome"]["banner"]

    RULES_CHANNEL_ID = 1394437098697916556   # zamijeni sa stvarnim ID pravila
    ANNOUNCEMENTS_CHANNEL_ID = 1393706033293168691  # zamijeni sa stvarnim ID obavještenja

    embed = discord.Embed(
        title=f"Dobrodošao {member.name} 👋",
        description=(
            f"**Dobrodošao {member.mention} na {member.guild.name}!** 🎉\n"
            f"Ovdje se igramo, družimo i poštujemo jedni druge! 💬\n\n"
            f"📌 **Obavezno:**\n"
            f"▸ Pročitaj pravila u <#{RULES_CHANNEL_ID}>\n"
            f"▸ Prati obavijesti u <#{ANNOUNCEMENTS_CHANNEL_ID}>\n"
            f"▸ Upoznaj nove prijatelje 👥\n\n"
            f"👑 **Founder:** BoSaNaC, GAG1\n"
            f"💼 **Vlasnici:** xsevy\n"
            f"🛡 **Discord Moderator:** BoSaNaC\n"
            f"🧰 **Server Moderator:** BoSaNaC"
        ),
        color=0x2ecc71
    )
    embed.set_thumbnail(url=logo)
    embed.set_image(url=banner)
    embed.set_footer(text=f"{member.guild.name} • Uživaj na serveru!", icon_url=logo)
    await channel.send(f"👋 Dobrodošao/la {member.mention}!", embed=embed)

# -------------------------------
# BAN KOMANDA
# -------------------------------
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member_id: int, vrijeme: str = None, *, razlog: str = "Nije naveden"):
    guild = ctx.guild
    member = guild.get_member(member_id)

    if not member:
        try:
            user = await bot.fetch_user(member_id)
        except discord.NotFound:
            await ctx.send("❌ Korisnik s tim ID-em nije pronađen.")
            return
    else:
        user = member

    await guild.ban(user, reason=razlog)
    await ctx.send(f"⛔ {user} je banan. Razlog: {razlog}")

    log_channel = guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(title="⛔ Korisnik je banan", color=0x2ecc71)
        embed.add_field(name="Korisnik", value=f"{user} ({user.id})", inline=False)
        embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
        embed.add_field(name="Razlog", value=razlog, inline=False)
        await log_channel.send(embed=embed)

    if vrijeme:
        jedinica = vrijeme[-1]
        broj = int(vrijeme[:-1])
        sekunde = broj * 60 * 60 if jedinica == "h" else broj * 60 if jedinica == "m" else broj
        await asyncio.sleep(sekunde)
        await guild.unban(user)
        await ctx.send(f"✅ {user} je unbanan (istek vremena).")

# -------------------------------
# KICK KOMANDA
# -------------------------------
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member_id: int, *, razlog: str = "Nije naveden"):
    guild = ctx.guild
    member = guild.get_member(member_id)
    if not member:
        await ctx.send("❌ Korisnik nije pronađen.")
        return

    await member.kick(reason=razlog)
    await ctx.send(f"👢 {member.mention} izbačen. Razlog: {razlog}")

# -------------------------------
# MUTE KOMANDA
# -------------------------------
@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member_id: int, vrijeme: str, *, razlog: str = "Nije naveden"):
    guild = ctx.guild
    member = guild.get_member(member_id)
    if not member:
        await ctx.send("❌ Korisnik nije pronađen.")
        return

    # Pronađi ili napravi "Muted" rolu
    mute_role = discord.utils.get(guild.roles, name="Muted")
    if not mute_role:
        mute_role = await guild.create_role(name="Muted")
        await ctx.send("✅ Kreirana je rola 'Muted'.")

        # Postavi zabrane za SVE kanale
        for channel in guild.channels:
            try:
                await channel.set_permissions(
                    mute_role,
                    send_messages=False,
                    send_messages_in_threads=False,
                    create_public_threads=False,
                    create_private_threads=False,
                    add_reactions=False,
                    speak=False,
                    stream=False,
                    connect=False,
                    use_voice_activation=False,
                    request_to_speak=False,
                    view_channel=True
                )
            except Exception as e:
                print(f"⚠️ Greška kod podešavanja permisija u kanalu {channel.name}: {e}")

    # Izračunaj vrijeme u sekundama
    jedinica = vrijeme[-1]
    broj = int(vrijeme[:-1])
    sekunde = broj * 60 * 60 if jedinica == "h" else broj * 60 if jedinica == "m" else broj

    # Dodaj rolu
    await member.add_roles(mute_role, reason=razlog)
    await ctx.send(f"🔇 {member.mention} je mjutan na {vrijeme}. Razlog: {razlog}")

    # Čekaj do isteka
    await asyncio.sleep(sekunde)

    # Ukloni rolu i javi
    await member.remove_roles(mute_role)
    await ctx.send(f"🔊 {member.mention} je unmjutan.")
    
# -------------------------------
# GIVEAWAY KOMANDA
# -------------------------------
active_giveaways = {}

@bot.command(name="gstart")
@commands.has_permissions(administrator=True)
async def gstart(ctx, *, args=None):
    """Pokreće giveaway: !gstart giveaway <nagrada> <trajanje_min> <broj_pobjednika>"""
    await ctx.message.delete()

    if not args:
        await ctx.author.send("❌ Format: !gstart giveaway <nagrada> <trajanje_min> <broj_pobjednika>")
        return

    try:
        parts = args.split()
        if parts[0].lower() != "giveaway":
            await ctx.author.send("❌ Moraš početi s giveaway!")
            return

        nagrada = " ".join(parts[1:-2])
        trajanje = int(parts[-2])
        broj_pobjednika = int(parts[-1])
    except Exception:
        await ctx.author.send("❌ Pogrešan format! Primjer: !gstart giveaway Nitro Boost 30 1")
        return

    logo = LINKOVI["giveaway"]["logo"]

    def make_embed(remaining, color=0x2ecc71, status="Aktivan"):
        embed = discord.Embed(
            title="🎁 GIVEAWAY!",
            description=(
                f"Reagiraj sa 🎉 da sudjeluješ!\n\n"
                f"🏆 **Nagrada:** {nagrada}\n"
                f"🎯 **Broj pobjednika:** {broj_pobjednika}\n"
                f"👤 **Pokrenuo:** {ctx.author.mention}\n\n"
                f"⏱ **Preostalo:** {remaining}\n"
                f"📌 **Status:** {status}"
            ),
            color=color,
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_thumbnail(url=logo)
        embed.set_footer(text="🎉 Reagiraj da sudjeluješ!")
        return embed

    total_seconds = trajanje * 60
    embed = make_embed(f"{trajanje} minuta")
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎉")

    active_giveaways[msg.id] = {"running": True}

    while total_seconds > 0 and active_giveaways[msg.id]["running"]:
        if total_seconds > 60:
            mins = total_seconds // 60
            await msg.edit(embed=make_embed(f"{mins} minuta"))
            await asyncio.sleep(60)
            total_seconds -= 60
        else:
            for sec in range(total_seconds, 0, -1):
                if not active_giveaways[msg.id]["running"]:
                    break
                await msg.edit(embed=make_embed(f"{sec} sekundi"))
                await asyncio.sleep(1)
            total_seconds = 0

    # Završetak
    msg = await ctx.channel.fetch_message(msg.id)
    users = []
    for reaction in msg.reactions:
        if str(reaction.emoji) == "🎉":
            async for user in reaction.users(limit=None):
                if not user.bot:
                    users.append(user)

    if not users:
        await ctx.send("⚠️ Nema sudionika za giveaway!")
        del active_giveaways[msg.id]
        return

    pobjednici = random.sample(users, min(broj_pobjednika, len(users)))
    mentions = ", ".join([u.mention for u in pobjednici])
    await msg.edit(embed=make_embed("✅ Giveaway završen!", color=0x2ecc71, status="Završen"))
    await ctx.send(f"🏆 Čestitamo {mentions}! Osvojili ste **{nagrada}**! 🎉")

    del active_giveaways[msg.id]

# -------------------------------
# END GIVEAWAY
# -------------------------------
@bot.command(name="end")
@commands.has_permissions(administrator=True)
async def end_giveaway(ctx):
    """Ručno završava giveaway i izvlači pobjednika"""
    if not active_giveaways:
        return

    last_id = list(active_giveaways.keys())[-1]
    active_giveaways[last_id]["running"] = False

    msg = await ctx.channel.fetch_message(last_id)
    logo = LINKOVI["giveaway"]["logo"]
    banner = LINKOVI["giveaway"]["banner"]

    users = []
    for reaction in msg.reactions:
        if str(reaction.emoji) == "🎉":
            async for user in reaction.users(limit=None):
                if not user.bot:
                    users.append(user)

    if not users:
        embed = discord.Embed(
            title="🛑 GIVEAWAY PREKINUT",
            description="⚠️ Giveaway završen — nema sudionika.",
            color=0x2ecc71
        )
        embed.set_thumbnail(url=logo)
        embed.set_image(url=banner)
        await msg.edit(embed=embed)
        del active_giveaways[last_id]
        return

    winner = random.choice(users)
    embed = discord.Embed(
        title="🛑 GIVEAWAY PREKINUT",
        description=f"🎉 **Pobjednik:** {winner.mention}\n🏆 **Giveaway je završen!**",
        color=0x2ecc71
    )
    embed.set_thumbnail(url=logo)
    embed.set_image(url=banner)
    embed.set_footer(text="🎉 Hvala svima koji su sudjelovali!")
    await msg.edit(embed=embed)
    await ctx.send(f"🏆 Čestitamo {winner.mention}! 🎉")
    del active_giveaways[last_id]

# -------------------------------
# REROLL KOMANDA
# -------------------------------
@bot.command(name="reroll")
@commands.has_permissions(administrator=True)
async def reroll(ctx, message_id: int):
    try:
        msg = await ctx.channel.fetch_message(message_id)
        users = []
        for reaction in msg.reactions:
            if str(reaction.emoji) == "🎉":
                async for user in reaction.users(limit=None):
                    if not user.bot:
                        users.append(user)
        if not users:
            await ctx.send("⚠️ Nema sudionika za reroll.")
            return
        winner = random.choice(users)
        await ctx.send(f"🔄 Novi pobjednik: {winner.mention}! 🎉")
    except Exception as e:
        await ctx.send(f"⚠️ Greška: {e}")

# -------------------------------
# POKRENI BOTA
# -------------------------------
bot.run(TOKEN)