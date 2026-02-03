import discord
from discord.ext import commands
import random
import os
import asyncio
import json
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread

# --- 1. THIẾT LẬP SERVER GIỮ BOT ONLINE (KEEP ALIVE) ---
app = Flask('')
@app.route('/')
def home(): return "Bot A-coin is live!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- 2. CẤU HÌNH BOT (Prefix A và a) ---
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix=['A', 'a'], intents=intents, help_command=None)

# --- 3. QUẢN LÝ DỮ LIỆU (Lưu trữ tiền và thời gian) ---
DATA_FILE = "users.json"

def load_data():
    if not os.path.exists(DATA_FILE): return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- 4. LỆNH HELP (HƯỚNG DẪN) ---
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="📜 DANH SÁCH LỆNH BOT A-COIN", color=discord.Color.gold())
    embed.add_field(name="💰 Kinh tế", value="`Acash`: Xem tiền\n`Adaily`: Quà 24h\n`Awork`: Làm việc (10p)", inline=False)
    embed.add_field(name="🎲 Giải trí", value="`Ataixiu [tiền]`: Cá cược 🪙", inline=False)
    embed.add_field(name="🛠️ Hệ thống", value="`Aclear [số]`: Xóa chat\n`Ahelp`: Xem lệnh", inline=False)
    await ctx.send(embed=embed)

# --- 5. CÁC LỆNH KIẾM TIỀN (DAILY & WORK) ---
@bot.command()
async def daily(ctx):
    data = load_data()
    uid = str(ctx.author.id)
    now = datetime.now()

    if uid in data and "last_daily" in data[uid]:
        last = datetime.strptime(data[uid]["last_daily"], "%Y-%m-%d %H:%M:%S")
        if now < last + timedelta(hours=24):
            rem = (last + timedelta(hours=24)) - now
            return await ctx.send(f"⏳ Quay lại sau {rem.seconds//3600}h {rem.seconds%3600//60}p!")

    if uid not in data: data[uid] = {"balance": 0}
    data[uid]["balance"] += 1000
    data[uid]["last_daily"] = now.strftime("%Y-%m-%d %H:%M:%S")
    save_data(data)
    await ctx.send(f"🧾 {ctx.author.mention} nhận **1000 🪙**. Tổng: **{data[uid]['balance']} 🪙**.")

@bot.command()
async def work(ctx):
    data = load_data()
    uid = str(ctx.author.id)
    now = datetime.now()

    if uid in data and "last_work" in data[uid]:
        last = datetime.strptime(data[uid]["last_work"], "%Y-%m-%d %H:%M:%S")
        if now < last + timedelta(minutes=10):
            rem = (last + timedelta(minutes=10)) - now
            return await ctx.send(f"⏳ Nghỉ ngơi thêm {rem.seconds//60} phút!")

    earned = random.randint(200, 600)
    if uid not in data: data[uid] = {"balance": 0}
    data[uid]["balance"] += earned
    data[uid]["last_work"] = now.strftime("%Y-%m-%d %H:%M:%S")
    save_data(data)
    await ctx.send(f"🏗️ Bạn nhận được **{earned} 🪙**. Tổng: **{data[uid]['balance']} 🪙**.")

@bot.command(name="cash")
async def _cash(ctx):
    data = load_data()
    bal = data.get(str(ctx.author.id), {}).get("balance", 0)
    await ctx.send(f"💰 Tài khoản của {ctx.author.mention}: **{bal} 🪙**.")

# --- 6. LỆNH TÀI XỈU (ĐÃ SỬA LỖI CẬP NHẬT TIỀN) ---
@bot.command()
async def taixiu(ctx, bet: int = None):
    if bet is None or bet <= 0: return await ctx.send("⚠️ Ví dụ: `Ataixiu 100`.")
    
    data = load_data()
    uid = str(ctx.author.id)
    if uid not in data: data[uid] = {"balance": 0}
    
    if bet > data[uid]["balance"]:
        return await ctx.send(f"❌ Bạn chỉ có **{data[uid]['balance']} 🪙**, không đủ cược!")

    await ctx.send(f"🎲 {ctx.author.mention} cược **{bet} 🪙**! Gõ `tài` hoặc `xỉu` (15s).")

    def check(m): return m.author == ctx.author and m.content.lower() in ['tài', 'xỉu', 'tai', 'xiu']
    try:
        msg = await bot.wait_for('message', check=check, timeout=15.0)
    except asyncio.TimeoutError: return await ctx.send("⌛ Hết thời gian!")

    choice = msg.content.lower().replace('à', 'a').replace('ỉ', 'i')
    d1, d2, d3 = random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)
    total = d1 + d2 + d3
    res = "tai" if 11 <= total <= 17 else "xiu"
    
    # XỬ LÝ CỘNG TRỪ TIỀN VÀ LƯU NGAY LẬP TỨC
    if choice == res:
        data[uid]["balance"] += bet # Cộng tiền thắng
        msg_res = f"🎉 Thắng! Nhận được **{bet} 🪙**."
    else:
        data[uid]["balance"] -= bet # Trừ tiền thua
        msg_res = f"😞 Thua! Bạn mất **{bet} 🪙**."
    
    save_data(data) # Lưu file users.json ngay sau khi ván đấu kết thúc
    await ctx.send(f"🎲 Kết quả: {d1}+{d2}+{d3} = **{total}** ({res.upper()})\n{msg_res} Số dư: **{data[uid]['balance']} 🪙**.")

# --- 7. KHỞI CHẠY ---
@bot.event
async def on_ready():
    print(f'==> {bot.user} online! Sẵn sàng phục vụ.')

if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv('TOKEN'))
