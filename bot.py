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

async def check_new_quests():
    global seen_quests
    url = "https://zealy.io/cw/mameinu/questboard"
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        new_quests = []
        keywords = ["Daily", "Raid", "Follow", "Like", "Retweet", "Join", "Visit", "Spread", 
                   "Connect", "Quote", "Mame", "Timeline", "Capsule"]
        
        for tag in soup.find_all(['h3','h4','div','span','a','p','strong']):
            text = tag.get_text(strip=True)
            if len(text) > 15 and any(k in text for k in keywords):
                quest_key = text[:150]
                if quest_key not in seen_quests:
                    seen_quests.add(quest_key)
                    new_quests.append(text)
        
        if new_quests:
            for q in new_quests[:5]:
                msg = f"""🚨 **QUEST MỚI - MAME INU** 🚨

📌 {q}

🔗 [Vào Questboard]({url})

⏰ {time.strftime('%H:%M %d/%m/%Y')}
"""
                await bot.send_message(CHAT_ID, msg, parse_mode="Markdown", disable_web_page_preview=True)
                await asyncio.sleep(2)
    except Exception as e:
        print("Lỗi:", e)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("✅ Bot Mame Inu Quest Alert đang chạy 24/7!")

async def scheduler():
    await check_new_quests()
    while True:
        await asyncio.sleep(240)
        await check_new_quests()

async def main():
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
