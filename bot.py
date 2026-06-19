import asyncio
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import time
import os

# ================== CONFIG ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
CHECK_INTERVAL = 60   # 60 giây
# ===========================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

seen_quests = set()   # Để phát hiện quest mới

async def get_all_quests():
    """Lấy tất cả quest hiện có trên Zealy"""
    url = "https://zealy.io/cw/mameinu/questboard"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        quests = []
        keywords = ["Daily", "Raid", "Mame", "Follow", "Visit", "Spread", "Connect", "Capsule", "Timeline"]
        
        for tag in soup.find_all(['h3', 'h4', 'div', 'span', 'a', 'p', 'strong']):
            text = tag.get_text(strip=True)
            if len(text) > 15 and any(k in text for k in keywords) and "Outline" not in text:
                # Loại bỏ lặp
                if text not in quests and len(text) < 200:
                    quests.append(text)
        
        return quests[:30]  # Giới hạn 30 quest để tránh spam
        
    except Exception as e:
        print(f"Lỗi lấy quest: {e}")
        return []

async def send_all_quests():
    quests = await get_all_quests()
    if not quests:
        await bot.send_message(CHAT_ID, "❌ Không lấy được danh sách quest. Thử lại sau.")
        return
    
    header = f"""📋 **TẤT CẢ NHIỆM VỤ HIỆN TẠI - MAME INU**
({len(quests)} quest đang có)

"""
    message = header
    for i, q in enumerate(quests, 1):
        message += f"{i}. {q}\n"
        if i % 15 == 0:  # Chia tin nhắn nếu quá dài
            await bot.send_message(CHAT_ID, message, parse_mode="Markdown", disable_web_page_preview=True)
            message = ""
            await asyncio.sleep(1)
    
    if message:
        await bot.send_message(CHAT_ID, message, parse_mode="Markdown", disable_web_page_preview=True)
    
    await bot.send_message(CHAT_ID, f"🔗 [Vào Questboard đầy đủ](https://zealy.io/cw/mameinu/questboard)", parse_mode="Markdown")

async def check_new_quests():
    global seen_quests
    quests = await get_all_quests()
    
    new_quests = []
    for q in quests:
        if q not in seen_quests:
            seen_quests.add(q)
            new_quests.append(q)
    
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
    await message.answer("✅ **Bot Mame Inu Quest** đang chạy!\n\nDùng lệnh /quests để xem tất cả nhiệm vụ hiện tại.")

@dp.message(Command("quests"))
async def quests_command(message: types.Message):
    await message.answer("🔍 Đang quét tất cả nhiệm vụ trên Zealy...")
    await send_all_quests()

async def scheduler():
    print("🚀 Bot đang chạy - Quét quest mỗi 60 giây")
    await check_new_quests()   # Quét lần đầu
    
    while True:
        await asyncio.sleep(CHECK_INTERVAL)
        await check_new_quests()

async def main():
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
        
