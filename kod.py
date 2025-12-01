import discord
from discord.ext import commands
import os
import random
import asyncio
from dotenv import load_dotenv

# ====================================================
# ENV AYARLARI
# ====================================================
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ====================================================
# LEVEL SİSTEMİ
# ====================================================
user_xp = {}

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    uid = message.author.id
    user_xp[uid] = user_xp.get(uid, 0) + random.randint(5, 15)

    level = int(user_xp[uid] ** 0.25)
    if user_xp[uid] % 100 == 0:
        await message.channel.send(f"🔥 {message.author.mention} **level {level}** olduuu!!")

    await bot.process_commands(message)

@bot.command()
async def level(ctx, member: discord.Member = None):
    member = member or ctx.author
    xp = user_xp.get(member.id, 0)
    lvl = int(xp ** 0.25)
    await ctx.send(f"{member.mention} **Level:** {lvl} | **XP:** {xp}")

# ====================================================
# EKONOMİ SİSTEMİ
# ====================================================
user_money = {}

@bot.command()
async def para(ctx):
    money = user_money.get(ctx.author.id, 0)
    await ctx.send(f"{ctx.author.mention}, hesabında **{money}💰** var.")

@bot.command()
async def çalış(ctx):
    kazanç = random.randint(50, 200)
    user_money[ctx.author.id] = user_money.get(ctx.author.id, 0) + kazanç
    await ctx.send(f"💼 Çalıştın ve **{kazanç}💰** kazandın!")

# ====================================================
# MODERASYON KOMUTLARI
# ====================================================
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, sebep="Sebep belirtilmedi"):
    await member.kick(reason=sebep)
    await ctx.send(f"🦵 {member} sunucudan atıldı!")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, sebep="Sebep belirtilmedi"):
    await member.ban(reason=sebep)
    await ctx.send(f"🔨 {member} sunucudan banlandı!")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def sil(ctx, miktar: int):
    await ctx.channel.purge(limit=miktar)
    await ctx.send(f"🧹 {miktar} mesaj temizlendi!", delete_after=3)

# ====================================================
# DM DUYURU KOMUTU
# ====================================================
@bot.command()
@commands.has_permissions(administrator=True)
async def dmduyuru(ctx, *, mesaj: str):
    count = 0
    for member in ctx.guild.members:
        if member.bot:
            continue
        try:
            await member.send(mesaj)
            count += 1
        except:
            pass
    await ctx.send(f"✅ Mesaj {count} kişiye DM olarak gönderildi.")

# ====================================================
# OTOMATİK ROL + HOŞ GELDİN
# ====================================================
@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name="🍄 | Üye")
    if role:
        try:
            await member.add_roles(role)
        except:
            pass

    embed = discord.Embed(
        title="🎉 Hoş Geldin!",
        description=f"{member.mention} sunucuya ışık gibi düştü!",
        color=0x00ffae
    )
    embed.set_thumbnail(url=member.display_avatar)
    embed.add_field(name="Verilen Rol:", value="⭐️・Member")

    log_ch = discord.utils.get(member.guild.text_channels, name="log-kanki̇-bura")
    if log_ch:
        await log_ch.send(embed=embed)

# ====================================================
# TICKET SİSTEMİ
# ====================================================
class CloseTicketView(discord.ui.View):
    def __init__(self, channel):
        super().__init__(timeout=None)
        self.channel = channel

    @discord.ui.button(label="Kapat", style=discord.ButtonStyle.red, emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket kapanıyor...", ephemeral=True)
        await self.channel.delete()

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def get_or_create_ticket_channel(self, interaction: discord.Interaction, message_text: str):
        guild = interaction.guild
        category_name = "・Kod Paylaşım・"
        channel_name = f"・🌙・destek-{interaction.user.name}"

        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            category = await guild.create_category(category_name)

        existing_channel = discord.utils.get(category.channels, name=channel_name)
        if existing_channel:
            await existing_channel.send(message_text)
            return existing_channel

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
        close_view = CloseTicketView(channel)
        await channel.send(f"{interaction.user.mention} ticket oluşturuldu! Aşağıdaki butonla kapatabilirsin.", view=close_view)
        await channel.send(message_text)
        return channel

    @discord.ui.button(label="Kod Şikayeti", style=discord.ButtonStyle.danger, emoji="⚠️")
    async def kod_sikayeti(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket açıldı, özel kanal oluşturuluyor...", ephemeral=True)
        await self.get_or_create_ticket_channel(interaction, f"{interaction.user.mention} Kod Şikayeti oluşturdu!")

    @discord.ui.button(label="Partnerlik Bilgi", style=discord.ButtonStyle.primary, emoji="❓")
    async def partnerlik_bilgi(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket açıldı, özel kanal oluşturuluyor...", ephemeral=True)
        await self.get_or_create_ticket_channel(interaction, f"{interaction.user.mention} Partnerlik Bilgi ticket'ı açtı!")

    @discord.ui.button(label="Admin Başvuru", style=discord.ButtonStyle.success, emoji="📝")
    async def admin_basvuru(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket açıldı, özel kanal oluşturuluyor...", ephemeral=True)
        await self.get_or_create_ticket_channel(interaction, f"{interaction.user.mention} Admin Başvuru ticket'ı açtı!")

    @discord.ui.button(label="Kod Hakkinda Sorular", style=discord.ButtonStyle.secondary, emoji="💡")
    async def kod_hakkinda_sorular(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket açıldı, özel kanal oluşturuluyor...", ephemeral=True)
        await self.get_or_create_ticket_channel(interaction, f"{interaction.user.mention} Kod Hakkinda Sorular ticket'ı açtı!")

# ====================================================
# ÇEKİLİŞ KOMUTU (!cekilisyap)
# ====================================================
@bot.command()
@commands.has_permissions(manage_messages=True)
async def cekilisyap(ctx):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    await ctx.send("🎁 Çekiliş başlıyor! **Ödülü yaz:**")
    ödül = await bot.wait_for("message", timeout=60, check=check)

    await ctx.send("⏱️ Süreyi yaz (10s / 5m / 2h):")
    süre = await bot.wait_for("message", timeout=60, check=check)

    await ctx.send("👤 Kaç kazanan olacak?")
    kazanan_sayisi = await bot.wait_for("message", timeout=60, check=check)
    kazanan_sayisi = int(kazanan_sayisi.content)

    await ctx.send("📢 **Çekiliş hangi kanala gönderilsin?**\n(#kanalı etiketle veya adını yaz)")
    kanal_msg = await bot.wait_for("message", timeout=60, check=check)

    if kanal_msg.channel_mentions:
        kanal = kanal_msg.channel_mentions[0]
    else:
        kanal = discord.utils.get(ctx.guild.text_channels, name=kanal_msg.content)

    if kanal is None:
        return await ctx.send("❌ Kanal bulunamadı!")

    süre_str = süre.content.lower()
    if süre_str.endswith("s"):
        saniye = int(süre_str[:-1])
    elif süre_str.endswith("m"):
        saniye = int(süre_str[:-1]) * 60
    elif süre_str.endswith("h"):
        saniye = int(süre_str[:-1]) * 3600
    else:
        return await ctx.send("❌ Süre biçimi yanlış!")

    embed = discord.Embed(
        title="🎉 ÇEKİLİŞ BAŞLADI!",
        description=f"**Ödül:** {ödül.content}\n"
                    f"**Süre:** {süre.content}\n"
                    f"**Kazanan:** {kazanan_sayisi}\n\n"
                    f"🎟️ Katılmak için 🎉 tepkisine bas!",
        color=0x00ff90
    )

    msg = await kanal.send(embed=embed)
    await msg.add_reaction("🎉")

    await ctx.send(f"✅ Çekiliş **{kanal.mention}** kanalına gönderildi!")

    await asyncio.sleep(saniye)

    msg = await kanal.fetch_message(msg.id)
    users = await msg.reactions[0].users().flatten()
    users = [u for u in users if not u.bot]

    if len(users) < kazanan_sayisi:
        return await kanal.send("❌ Yeterli katılım yok, çekiliş iptal!")

    kazananlar = random.sample(users, kazanan_sayisi)
    kazan_yazi = ", ".join([k.mention for k in kazananlar])

    await kanal.send(f"🎉 **ÇEKİLİŞ BİTTİ!**\n🏆 Kazananlar: {kazan_yazi}\n🎁 Ödül: **{ödül.content}**")

# ====================================================
# BOT READY + TICKET MESAJI
# ====================================================
@bot.event
async def on_ready():
    print("\n" + "═" * 40)
    print(f"✅ BOT AKTİF: {bot.user}")
    print(f"🌐 Sunucu sayısı: {len(bot.guilds)}")
    print("═" * 40 + "\n")

    guild = bot.guilds[0]
    category = discord.utils.get(guild.categories, name="・Kod #DESTEK・")
    if not category:
        category = await guild.create_category("・Kod #DESTEK・")

    channel = discord.utils.get(category.channels, name="・🌙・destek")
    if not channel:
        channel = await guild.create_text_channel("・🌙・destek", category=category)

    view = TicketView()
    ticket_message = "Kod Paylaşım Ticket Oluştur\nHizmet Saatleri: 18.00 - 21.00"
    await channel.send(ticket_message, view=view)

# ====================================================
# KOD PAYLAŞIM KOMUTU
# ====================================================
@bot.command()
async def kodpaylas(ctx):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    # Dil sor
    await ctx.send("💻 Hangi dilde kod paylaşmak istiyorsun? (örnek: js, html, python)")
    dil_msg = await bot.wait_for("message", timeout=60, check=check)
    dil = dil_msg.content.lower()

    # Kanal sor
    await ctx.send("📂 Kod hangi kanala gönderilsin? (#kanalı etiketle veya adını yaz)")
    kanal_msg = await bot.wait_for("message", timeout=60, check=check)

    if kanal_msg.channel_mentions:
        kanal = kanal_msg.channel_mentions[0]
    else:
        kanal = discord.utils.get(ctx.guild.text_channels, name=kanal_msg.content)

    if kanal is None:
        return await ctx.send("❌ Kanal bulunamadı!")

    # Gerçek işe yarar kod örnekleri
    kodlar = {
        "js": [
            "document.querySelector('button').addEventListener('click', () => alert('Tıklandı!'));",
            "fetch('https://api.coindesk.com/v1/bpi/currentprice.json').then(res => res.json()).then(data => console.log(data));",
            "function topla(a, b) { return a + b; } console.log(topla(5, 10));"
        ],
        "html": [
            "<form><input type='text' placeholder='Adınız'><button>Gönder</button></form>",
            "<table border='1'><tr><th>Ad</th><th>Yaş</th></tr><tr><td>Yiğit</td><td>18</td></tr></table>",
            "<button onclick=\"document.body.style.background='yellow'\">Sarı Yap</button>"
        ],
        "python": [
            "with open('deneme.txt', 'w') as f:\n    f.write('Merhaba!')",
            "x = [1,2,3,4]; print([i*2 for i in x])",
            "def faktoriyel(n): return 1 if n==0 else n*faktoriyel(n-1)\nprint(faktoriyel(5))"
        ]
    }

    if dil not in kodlar:
        return await ctx.send("❌ Bu dil için örnek kod bulunamadı!")

    rastgele_kod = random.choice(kodlar[dil])

    embed = discord.Embed(
        title=f"{ctx.author} tarafından {dil.upper()} kod paylaşıldı",
        description=f"```{dil}\n{rastgele_kod}\n```",
        color=0x00ff90
    )
    await kanal.send(embed=embed)
    await ctx.send(f"✅ Kod {kanal.mention} kanalına gönderildi!")
    
# ====================================================
# SESLİ KANALA GİR KOMUTU (!join)
# ====================================================
@bot.command()
async def join(ctx):
    # Kullanıcının ses kanalında olup olmadığını kontrol et
    if ctx.author.voice is None:
        await ctx.send("❌ Önce bir ses kanalına girmen gerekiyor!")
        return

    kanal = ctx.author.voice.channel

    # Botun kanala katılması veya taşıması
    if ctx.voice_client is not None:
        await ctx.voice_client.move_to(kanal)
    else:
        await kanal.connect()

    await ctx.send(f"✅ {bot.user.name} kanala katıldı: {kanal.name}")

bot.run(TOKEN)
