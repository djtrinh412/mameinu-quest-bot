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
# ===========================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

seen_quests = set()

async def send_test_message():
    """Gửi tin nhắn test ngay khi bot start"""
    try:
        await bot.send_message(CHAT_ID, "🔥 **BOT TEST** 🔥\n\nBot Mame Inu đã khởi động thành công!\nKiểm tra quest mỗi 3 phút.", parse_mode="Markdown")
        print("✅ Đã gửi tin nhắn test vào channel")
    except Exception as e:
        print(f"❌ Lỗi gửi test message: {e}")

async def check_new_quests():
    global seen_quests
    url = "https://zealy.io/cw/mameinu/questboard"
    print(f"[{time.strftime('%H:%M:%S')}] Đang quét quest...")

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=20)
        print(f"   Status code: {resp.status_code}")

        soup = BeautifulSoup(resp.text, 'html.parser')
        new_quests = []

        keywords = ["Daily", "Raid", "Follow", "Like", "Retweet", "Visit", "Mame", "Spread", "Connect"]

        for tag in soup.find_all(['h3','h4','div','span','a','p','strong']):
            text = tag.get_text(strip=True)
            if len(text) > 12 and any(k in text for k in keywords):
                quest_key = text[:100]
                if quest_key not in seen_quests:
                    seen_quests.add(quest_key)
                    new_quests.append(text)
                    print(f"   Phát hiện quest mới: {text[:60]}...")

        if new_quests:
            print(f"📢 Tìm thấy {len(new_quests)} quest mới!")
            for q in new_quests[:5]:
                msg = f"""🚨 **QUEST MỚI - MAME INU** 🚨

📌 {q}

🔗 [Vào Questboard]({url})

⏰ {time.strftime('%H:%M %d/%m')}
"""
                await bot.send_message(CHAT_ID, msg, parse_mode="Markdown", disable_web_page_preview=True)
                await asyncio.sleep(2)
        else:
            print("   Không có quest mới.")

    except Exception as e:
        print(f"❌ Lỗi quét quest: {e}")

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("✅ Bot Mame Inu Quest Alert đang chạy!\nDebug mode bật.")

async def scheduler():
    await send_test_message()   # Gửi test ngay
    await check_new_quests()    # Quét lần đầu
    
    while True:
        await asyncio.sleep(180)   # 3 phút
        await check_new_quests()

async def main():
    print("🚀 Bot đang khởi động...")
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
