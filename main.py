import discord
from discord.ext import commands
import random
import os
import asyncio
from flask import Flask
from threading import Thread

# --- 1. CẤU HÌNH WEB SERVER ĐỂ GIỮ BOT LUÔN THỨC (KEEP ALIVE) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. KHỞI TẠO BOT VỚI PREFIX 'O' IN HOA ---
intents = discord.Intents.default()
intents.message_content = True  # Bắt buộc phải bật trong Discord Developer Portal
bot = commands.Bot(command_prefix='O', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot {bot.user} đã sẵn sàng và online!')

# --- 3. CÁC LỆNH CƠ BẢN ---
@bot.command()
async def ping(ctx):
    """Kiểm tra độ trễ"""
    await ctx.send(f'🏓 Pong! {round(bot.latency * 1000)}ms')

@bot.command()
async def hello(ctx):
    """Chào hỏi"""
    await ctx.send(f'Chào {ctx.author.mention}!')

# --- 4. LỆNH LÀM SẠCH KÊNH (CLEAR) ---
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    """Xóa số lượng tin nhắn chỉ định (Ví dụ: Oclear 10)"""
    if amount <= 0:
        await ctx.send("Vui lòng nhập số lượng tin nhắn cần xóa lớn hơn 0.")
        return
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'🗑️ Đã xóa {len(deleted)-1} tin nhắn!', delete_after=5)

# --- 5. LỆNH CHƠI TÀI XỈU ---
@bot.command()
async def taixiu(ctx, bet_amount: int):
    """Chơi Tài Xỉu (Ví dụ: Otaixiu 100)"""
    if bet_amount <= 0:
        await ctx.send("Số tiền cược phải lớn hơn 0.")
        return

    await ctx.send(f"{ctx.author.mention}, bạn cược **{bet_amount}**! Hãy gõ `tài` hoặc `xỉu` trong 15s để đặt cửa.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['tài', 'xỉu']

    try:
        msg = await bot.wait_for('message', check=check, timeout=15.0)
    except asyncio.TimeoutError:
        await ctx.send(f"⌛ {ctx.author.mention}, hết thời gian đặt cửa. Ván đấu bị hủy.")
        return

    user_choice = msg.content.lower()
    await ctx.send(f"🎲 {ctx.author.mention} chọn **{user_choice.upper()}**. Đang lắc xúc xắc...")
    await asyncio.sleep(2)

    d1, d2, d3 = random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)
    total = d1 + d2 + d3
    result_type = "tài" if 11 <= total <= 17 else "xỉu"

    res_msg = f"🎰 Kết quả: {d1} + {d2} + {d3} = **{total}** ({result_type.upper()})\n"
    if user_choice == result_type:
        res_msg += f"🎉 Chúc mừng! Bạn thắng **{bet_amount * 2}**!"
    else:
        res_msg += f"😞 Rất tiếc! Bạn đã mất **{bet_amount}**."
    
    await ctx.send(res_msg)

# --- 6. CHẠY BOT ---
if __name__ == "__main__":
    keep_alive()  # Chạy Flask server
    # Render sẽ lấy Token từ mục Environment Variables
    TOKEN = os.getenv('TOKEN') 
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Lỗi: Chưa cài đặt TOKEN trong Environment Variables trên Render!")
