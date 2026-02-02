import discord
from discord.ext import commands
import random
import os
from flask import Flask
from threading import Thread

# 1. Tạo Server Web nhỏ để Render không tắt bot
app = Flask('')
@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. Cấu hình Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='o', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot {bot.user} đã sẵn sàng!')

# --- CÁC LỆNH CỦA BẠN ---
@bot.command()
async def ping(ctx):
    await ctx.send(f'🏓 Pong! {round(bot.latency * 1000)}ms')

@bot.command()
async def flip(ctx):
    result = random.choice(["Mặt Sấp", "Mặt Ngửa"])
    await ctx.send(f"🪙 Kết quả là: **{result}**")

@bot.command()
async def pick(ctx, *, choices: str):
    options = choices.split(",")
    selection = random.choice(options)
    await ctx.send(f"🤔 Mình chọn: **{selection.strip()}**")

# --- CHẠY BOT ---
if __name__ == "__main__":
    keep_alive() # Chạy server web song song với bot
    TOKEN = os.getenv('TOKEN')
    bot.run(TOKEN) # Dòng này đã được sửa lỗi ngoặc
