import discord
from discord.ext import commands
import random
import os
import asyncio
import json
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread

# --- 1. THIẾT LẬP WEB SERVER ĐỂ GIỮ BOT LUÔN CHẠY (KEEP ALIVE) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot A-coin is live and running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. KHỞI TẠO BOT VỚI PREFIX 'A' VÀ 'a' ---
intents = discord.Intents.default()
intents.message_content = True  # Cho phép đọc lệnh từ tin nhắn
bot = commands.Bot(command_prefix=['A', 'a'], intents=intents)

# --- 3. QUẢN LÝ HỆ THỐNG DỮ LIỆU ACOIN ---
DATA_FILE = "users.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- 4. CÁC LỆNH HỆ THỐNG ACOIN ---

@bot.command()
async def daily(ctx):
    """Nhận 1000 acoin mỗi 24h (Adaily/adaily)"""
    data = load_data()
    user_id = str(ctx.author.id)
    now = datetime.now()

    # Kiểm tra nếu người dùng đã daily trong vòng 24 giờ qua
    if user_id in data and "last_daily" in data[user_id]:
        last_daily = datetime.strptime(data[user_id]["last_daily"], "%Y-%m-%d %H:%M:%S")
        if now < last_daily + timedelta(hours=24):
            remaining = (last_daily + timedelta(hours=24)) - now
            hours, remainder = divmod(remaining.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return await ctx.send(f"⏳ {ctx.author.mention}, bạn đã nhận quà rồi! Hãy quay lại sau **{hours} giờ {minutes} phút**.")

    # Khởi tạo dữ liệu nếu là người dùng mới
    if user_id not in data:
        data[user_id] = {"balance": 0}
    
    # Cộng tiền và lưu thời gian thực hiện lệnh
    data[user_id]["balance"] = data[user_id].get("balance", 0) + 1000
    data[user_id]["last_daily"] = now.strftime("%Y-%m-%d %H:%M:%S")
    save_data(data)

    await ctx.send(f"🧾 {ctx.author.mention} đã nhận **1000 🪙** quà điểm danh! Hiện có: **{data[user_id]['balance']} 🪙**.")

@bot.command(name="cash")
async def _cash(ctx):
    """Lệnh Acash/acash để kiểm tra tiền"""
    data = load_data()
    bal = data.get(str(ctx.author.id), {}).get("balance", 0)
    await ctx.send(f"💰 Tài khoản của {ctx.author.mention} hiện đang có: **{bal} 🪙**.")

# --- 5. LỆNH TÀI XỈU (CHẶN NẾU KHÔNG ĐỦ TIỀN) ---
@bot.command()
async def taixiu(ctx, bet: int = None):
    """Chơi Tài Xỉu đặt cược acoin (VD: Ataixiu 100)"""
    if bet is None or bet <= 0:
        return await ctx.send("⚠️ Cách chơi: `Ataixiu [số 🪙]`. Ví dụ: `Ataixiu 100`")
    
    data = load_data()
    user_id = str(ctx.author.id)
    user_bal = data.get(user_id, {}).get("balance", 0)

    # Kiểm tra số dư chặt chẽ trước khi chơi
    if bet > user_bal:
        return await ctx.send(f"❌ {ctx.author.mention}, bạn không đủ 🪙! Số dư hiện tại: **{user_bal} 🪙**.")

    await ctx.send(f"🎲 {ctx.author.mention} đặt cược **{bet} 🪙**! Hãy gõ `tài` hoặc `xỉu` trong 15s.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['tài', 'xỉu', 'tai', 'xiu']

    try:
        msg = await bot.wait_for('message', check=check, timeout=15.0)
    except asyncio.TimeoutError:
        return await ctx.send(f"⌛ {ctx.author.mention}, đã quá thời gian đặt cửa! Ván đấu hủy.")

    user_choice = msg.content.lower().replace('à', 'a').replace('ỉ', 'i')
    await ctx.send("🎰 Đang lắc xúc xắc...")
    await asyncio.sleep(2)

    d1, d2, d3 = random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)
    total = d1 + d2 + d3
    result = "tai" if 11 <= total <= 17 else "xiu"

    output = f"🎲 Kết quả: {d1} + {d2} + {d3} = **{total}** ({result.upper()})\n"
    
    if user_choice == result:
        data[user_id]["balance"] += bet
        output += f"🎉 Thắng lớn! Bạn nhận được **{bet * 2} 🪙**. Số dư: **{data[user_id]['balance']} 🪙**."
    await ctx.send(output)

# --- 6. LỆNH LÀM SẠCH KÊNH (CLEAR) ---
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    """Xóa tin nhắn gần nhất (VD: Aclear 10)"""
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🗑️ Đã xóa {amount} tin nhắn!", delete_after=3)

# --- 7. SỰ KIỆN KHỞI ĐỘNG VÀ CHẠY BOT ---
@bot.event
async def on_ready():
    print(f'==> Bot {bot.user} đã sẵn sàng với Prefix A/a và đơn vị acoin!')

if __name__ == "__main__":
    keep_alive()  # Chạy Flask server để Render không tắt bot
    # Lấy Token từ Environment Variables trên Render
    token = os.getenv('TOKEN')
    if token:
        bot.run(token)
    else:
        print("Lỗi: Chưa cài đặt TOKEN!")
