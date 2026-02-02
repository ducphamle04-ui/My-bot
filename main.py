import discord
from discord.ext import commands
import random

# 1. Cấu hình Intents (Quyền hạn)
intents = discord.Intents.default()
intents.message_content = True  # Quan trọng: Phải bật cái này trên Developer Portal
intents.members = True          # Quyền xem thông tin thành viên

# 2. Khởi tạo Bot với Prefix 'o'
bot = commands.Bot(command_prefix='O', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot {bot.user} đã sẵn sàng!')

# --- TÍNH NĂNG NHẮN TIN THEO YÊU CẦU ---

@bot.event
async def on_message(message):
    # Đừng để bot tự trả lời chính nó (tránh lặp vô tận)
    if message.author == bot.user:
        return

    # Kiểm tra nếu nội dung tin nhắn có chứa "@aarondeptroai#0000"
    # Lưu ý: Discord thường dùng ID thay vì tag chữ, nhưng bot vẫn có thể quét nội dung text
    if "ron oi" in message.content:
        await message.channel.send("ron con cak")

    # Dòng này cực kỳ quan trọng: Cho phép các lệnh prefix (ohello, oflip...) vẫn chạy được
    await bot.process_commands(message)

# --- CÁC LỆNH PREFIX 'o' ---

@bot.command()
async def hello(ctx):
    await ctx.send(f'Chào {ctx.author.mention}!')

@bot.command()
async def flip(ctx):
    result = random.choice(["Mặt Sấp", "Mặt Ngửa"])
    await ctx.send(f"🪙 Kết quả là: **{result}**")

@bot.command()
async def pick(ctx, *, choices: str):
    options = choices.split(",")
    selection = random.choice(options)
    await ctx.send(f"🤔 Mình chọn: **{selection.strip()}**")

# --- DÁN TOKEN MỚI VÀO ĐÂY ---
import os

# Lấy Token từ môi trường hệ thống (Environment Variable)
TOKEN = os.getenv('TOKEN')

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Lỗi: Không tìm thấy TOKEN trong Environment Variables!")


if __name__ == "__main__":
   bot.run(os.getenv((TOKEN))
           
