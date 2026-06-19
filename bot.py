import asyncio
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import time
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def get_quests():
    try:
        url = "https://zealy.io/cw/mameinu/questboard"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        quests = []
        for tag in soup.find_all(['h3', 'h4', 'div', 'span']):
            text = tag.get_text(strip=True)
            if len(text) > 15 and ("Daily" in text or "Raid" in text or "Mame" in text or "Follow" in text or "Visit" in text):
                if text not in quests:
                    quests.append(text)
        return quests[:20]
    except:
        return []

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("✅ Bot running.\nUse /quests")

@dp.message(Command("quests"))
async def send_quests(message: types.Message):
    await message.answer("🔍 Đang lấy danh sách quest...")
    quests = get_quests()
    
    if not quests:
        await message.answer("❌ Không lấy được quest lúc này.\n\n🔗 https://zealy.io/cw/mameinu/questboard")
        return
    
    text = "📋 **MAME INU QUESTS**\n\n"
    for i, q in enumerate(quests, 1):
        text += f"{i}. {q}\n\n"
    
    text += f"🔗 Full: https://zealy.io/cw/mameinu/questboard\n⏰ {time.strftime('%H:%M %d/%m')}"
    
    await message.answer(text, parse_mode="Markdown", disable_web_page_preview=True)

async def main():
    print("Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
