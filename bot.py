import asyncio
import requests
import time
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import os

# ================== CONFIG ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
CHECK_INTERVAL = 60
SUBDOMAIN = "mameinu"
# ===========================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

seen_quests = set()

def get_all_quests():
    url = f"https://api-v2.zealy.io/public/communities/{SUBDOMAIN}/quests"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code != 200:
            print(f"API lỗi: {resp.status_code}")
            return []
        
        data = resp.json()
        quests = []
        
        for quest in data.get("quests", []):
            title = quest.get("name") or quest.get("title")
            if title:
                quests.append(title.strip())
        
        return quests[:30]
        
    except Exception as e:
        print(f"Lỗi API: {e}")
        return []

async def send_all_quests():
    await bot.send_message(CHAT_ID, "🔍 Đang lấy danh sách nhiệm vụ từ Zealy API...")
    quests = get_all_quests()
    
    if not quests:
        await bot.send_message(CHAT_ID, "❌ Hiện tại không lấy được quest. Thử lại sau.")
        return
    
    header = f"""📋 **TẤT CẢ NHIỆM VỤ - MAME INU**
({len(quests)} quest)

"""
    message = header
    for i, q in enumerate(quests, 1):
        message += f"**{i}.** {q}\n\n"
        if len(message) > 3500 or i % 12 == 0:
            await bot.send_message(CHAT_ID, message, parse_mode="Markdown")
            message = ""
            await asyncio.sleep(1)
    
    if message:
        await bot.send_message(CHAT_ID, message, parse_mode="Markdown")
    
    await bot.send_message(CHAT_ID, "🔗 [Mở Questboard](https://zealy.io/cw/mameinu/questboard)", parse_mode="Markdown")

async def check_new_quests():
    global seen_quests
    quests = get_all_quests()
    new_quests = [q for q in quests if q not in seen_quests]
    
    for q in new_quests:
        seen_quests.add(q)
    
    if new_quests:
        print(f"🚨 Phát hiện {len(new_quests)} quest mới!")
        for q in new_quests[:5]:
            msg = f"""🚨 **QUEST MỚI - MAME INU** 🚨

📌 {q}

🔗 [Tham gia ngay](https://zealy.io/cw/mameinu/questboard)

⏰ {time.strftime('%H:%M:%S %d/%m')}
"""
            await bot.send_message(CHAT_ID, msg, parse_mode="Markdown", disable_web_page_preview=True)
            await asyncio.sleep(2)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("✅ **Bot Mame Inu Quest** đang chạy tốt!\nDùng /quests để xem tất cả nhiệm vụ.")

@dp.message(Command("quests"))
async def quests_command(message: types.Message):
    await send_all_quests()

async def scheduler():
    print("🚀 Bot API khởi động - Quét mỗi 60 giây")
    await check_new_quests()
    while True:
        await asyncio.sleep(CHECK_INTERVAL)
        await check_new_quests()

async def main():
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
