import discord
from discord.ext import commands
import random
import os
import asyncio
import json
from flask import Flask
from threading import Thread

# --- 1. THIẾT LẬP WEB SERVER ĐỂ GIỮ BOT LUÔN CHẠY (KEEP ALIVE) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot A-coin is live and running!"

def run():
    # Render yêu cầu chạy trên cổng 8080 để nhận diện dịch vụ web
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. KHỞI TẠO BOT VỚI PREFIX 'A' VÀ 'a' ---
intents = discord.Intents.default()
intents.message_content = True  # Bật để bot đọc được lệnh từ tin nhắn
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

def get_balance(user_id):
    data = load_data()
    return data.get(str(user_id), 0)

def update_balance(user_id, amount):
    data = load_data()
    uid = str(user_id)
    data[uid] = data.get(uid, 0) + amount
    save_data(data)

# --- 4. CÁC LỆNH HỆ THỐNG ACOIN ---

@bot.command()
async def daily(ctx):
    """Nhận acoin hằng ngày (Adaily hoặc adaily)"""
    amount = 1000
    update_balance(ctx.author.id, amount)
    await ctx.send(f"✅ {ctx.author.mention} đã nhận **{amount} acoin** quà điểm danh! Hiện có: **{get_balance(ctx.author.id)} acoin**.")

@bot.command(name="cash")
async def _cash(ctx):
    """Lệnh Acash hoặc acash để kiểm tra tiền"""
    bal = get_balance(ctx.author.id)
    await ctx.send(f"💰 Tài khoản của {ctx.author.mention} hiện đang có: **{bal} acoin**.")

# --- 5. LỆNH TÀI XỈU (CHẶN NẾU KHÔNG ĐỦ TIỀN) ---
@bot.command()
async def taixiu(ctx, bet: int = None):
    """Chơi Tài Xỉu đặt cược acoin (VD: Ataixiu 100)"""
    # Kiểm tra nếu người dùng không nhập tiền hoặc nhập sai
    if bet is None or bet <= 0:
        return await ctx.send("⚠️ Cách chơi: `Ataixiu [số acoin]`. Ví dụ: `Ataixiu 100`")
    
    # KIỂM TRA SỐ DƯ: Không có tiền hoặc không đủ tiền sẽ không cho chơi
    user_bal = get_balance(ctx.author.id)
    if bet > user_bal:
        return await ctx.send(f"❌ {ctx.author.mention}, bạn không đủ acoin! Số dư hiện tại: **{user_bal} acoin**.")

    await ctx.send(f"🎲 {ctx.author.mention} đặt cược **{bet} acoin**! Hãy gõ `tài` hoặc `xỉu` trong 15 giây.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['tài', 'xỉu', 'tai', 'xiu']

    try:
        # Chờ phản hồi chọn cửa từ người chơi
        msg = await bot.wait_for('message', check=check, timeout=15.0)
    except asyncio.TimeoutError:
        return await ctx.send(f"⌛ {ctx.author.mention}, bạn đã quá thời gian đặt cửa! Ván đấu bị hủy.")

    user_choice = msg.content.lower().replace('à', 'a').replace('ỉ', 'i')
    await ctx.send("🎰 Đang lắc xúc xắc...")
    await asyncio.sleep(2)

    d1, d2, d3 = random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)
    total = d1 + d2 + d3
    result = "tai" if 11 <= total <= 17 else "xiu"

    output = f"🎲 Kết quả: {d1} + {d2} + {d3} = **{total}** ({result.upper()})\n"
    
    if user_choice == result:
        update_balance(ctx.author.id, bet)
        output += f"🎉 Thắng lớn! Bạn nhận được **{bet * 2} acoin**. Số dư: **{get_balance(ctx.author.id)} acoin**."
    else:
        update_balance(ctx.author.id, -bet)
        output += f"😞 Rất tiếc! Bạn đã mất **{bet} acoin**. Số dư: **{get_balance(ctx.author.id)} acoin**."
    
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
