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
CHECK_INTERVAL = 60   # ← Quét mỗi 60 giây (1 phút)
# ===========================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

seen_quests = set()

async def send_status():
    try:
        await bot.send_message(CHAT_ID, f"🔄 Bot đang quét quest mỗi {CHECK_INTERVAL} giây...", parse_mode="Markdown")
    except:
        pass

async def check_new_quests():
    global seen_quests
    url = "https://zealy.io/cw/mameinu/questboard"
    print(f"[{time.strftime('%H:%M:%S')}] 🔍 Đang quét Zealy...")

    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        resp = requests.get(url, headers=headers, timeout=15)
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        new_quests = []
        keywords = ["Daily", "Raid", "Follow", "Like", "Retweet", "Visit", "Mame", "Spread", "Connect", "Quote", "Capsule"]

        for tag in soup.find_all(['h3','h4','div','span','a','p','strong']):
            text = tag.get_text(strip=True)
            if len(text) > 15 and any(k in text for k in keywords):
                quest_key = text[:120]
                if quest_key not in seen_quests:
                    seen_quests.add(quest_key)
                    new_quests.append(text)
                    print(f"   ✅ Phát hiện quest mới: {text[:70]}...")

        if new_quests:
            print(f"🚨 Tìm thấy {len(new_quests)} quest mới!")
            for q in new_quests[:6]:
                msg = f"""🚨 **QUEST MỚI - MAME INU** 🚨

📌 {q}

🔗 [Tham gia ngay]({url})

⏰ {time.strftime('%H:%M:%S %d/%m')}
"""
                await bot.send_message(CHAT_ID, msg, parse_mode="Markdown", disable_web_page_preview=True)
                await asyncio.sleep(1.5)
        else:
            print("   Không có quest mới.")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(f"✅ **Bot Mame Inu Quest Alert**\nQuét quest mỗi {CHECK_INTERVAL} giây - Đang chạy tốt!")

async def scheduler():
    await send_status()
    await check_new_quests()   # Quét ngay khi start
    
    while True:
        await asyncio.sleep(CHECK_INTERVAL)
        await check_new_quests()

async def main():
    print("🚀 Bot Mame Inu đã khởi động - Tốc độ quét: 60 giây")
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
