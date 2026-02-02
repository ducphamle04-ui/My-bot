import discord
from discord.ext import commands
import random
import os
import asyncio
from flask import Flask
from threading import Thread

# --- 1. KEEP ALIVE SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot is live!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- 2. CONFIG BOT (Prefix O hoa) ---
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix='O', intents=intents)

@bot.event
async def on_ready():
    print(f'==> Bot {bot.user} da san sang!')

# --- 3. LENH TAI XIU (Da sua loi thieu tham so) ---
@bot.command()
async def taixiu(ctx, bet: int = None):
    if bet is None:
        await ctx.send("⚠️ Ban quen nhap tien cuoc roi! Vi du: `Otaixiu 100`")
        return
    
    await ctx.send(f"🎲 {ctx.author.mention} cuoc **{bet}**! Go `tai` hoac `xiu` trong 15s.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['tai', 'xiu', 'tài', 'xỉu']

    try:
        msg = await bot.wait_for('message', check=check, timeout=15.0)
    except asyncio.TimeoutError:
        await ctx.send(f"⌛ {ctx.author.mention} het thoi gian!")
        return

    choice = msg.content.lower().replace('à', 'a').replace('ỉ', 'i') # Chuan hoa tai/xiu
    await ctx.send("🎰 Dang lac...")
    await asyncio.sleep(2)

    d1, d2, d3 = random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)
    total = d1 + d2 + d3
    res = "tai" if 11 <= total <= 17 else "xiu"

    output = f"🎲 Ket qua: {d1}+{d2}+{d3} = **{total}** ({res.upper()})\n"
    if choice == res:
        output += f"🎉 Thang! Nhan **{bet * 2}**!"
    else:
        output += f"😞 Thua roi!"
    await ctx.send(output)

# --- 4. LENH CLEAR ---
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🗑 Da xoa {amount} tin nhan!", delete_after=3)

# --- 5. RUN ---
if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv('TOKEN'))
