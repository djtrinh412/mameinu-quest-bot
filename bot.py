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
CHECK_INTERVAL = 60
# ===========================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

seen_quests = set()

async def get_all_quests():
    url = "https://zealy.io/cw/mameinu/questboard"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        quests = []
        # Tìm tất cả text tiềm năng là quest title
        for tag in soup.find_all(['h3', 'h4', 'div', 'span', 'a', 'p', 'strong']):
            text = tag.get_text(strip=True)
            
            # Điều kiện rộng hơn để bắt hết quest
            if (len(text) > 8 and 
                not any(skip in text for skip in ["All Outline", "All", "0 /", "Outline", "Your privacy", "Cookie", "Join the community"])):
                
                # Loại bỏ text lặp và quá ngắn
                if text not in quests and len(text) < 180:
                    quests.append(text)
        
        # Ưu tiên các quest có emoji hoặc từ khóa rõ
        priority = []
        normal = []
        for q in quests:
            if any(k in q for k in ["📆", "💊", "🐾", "🎨", "Daily", "Raid", "Mame"]):
                priority.append(q)
            else:
                normal.append(q)
        
        return priority + normal[:25]  # Giới hạn tránh spam
        
    except Exception as e:
        print(f"Lỗi lấy quest: {e}")
        return []

async def send_all_quests():
    quests = await get_all_quests()
    if not quests:
        await bot.send_message(CHAT_ID, "❌ Vẫn chưa lấy được quest. Thử lại sau ít phút.")
        return
    
    header = f"""📋 **TẤT CẢ NHIỆM VỤ HIỆN TẠI - MAME INU**
({len(quests)} quest)

"""
    message = header
    for i, q in enumerate(quests, 1):
        message += f"**{i}.** {q}\n\n"
        if len(message) > 3500 or i % 12 == 0:   # Chia tin nhắn
            await bot.send_message(CHAT_ID, message, parse_mode="Markdown", disable_web_page_preview=True)
            message = ""
            await asyncio.sleep(1)
    
    if message:
        await bot.send_message(CHAT_ID, message, parse_mode="Markdown", disable_web_page_preview=True)
    
    await bot.send_message(CHAT_ID, "🔗 [Mở Questboard đầy đủ](https://zealy.io/cw/mameinu/questboard)", parse_mode="Markdown")

async def check_new_quests():
    global seen_quests
    quests = await get_all_quests()
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
    await message.answer("✅ **Bot Mame Inu Quest** đang chạy!\n/quêtes để xem tất cả nhiệm vụ.")

@dp.message(Command("quests"))
async def quests_command(message: types.Message):
    await message.answer("🔍 Đang quét tất cả nhiệm vụ...")
    await send_all_quests()

async def scheduler():
    print("🚀 Bot khởi động - Quét mỗi 60 giây")
    await check_new_quests()
    while True:
        await asyncio.sleep(CHECK_INTERVAL)
        await check_new_quests()

async def main():
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
        
