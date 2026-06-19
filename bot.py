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

def get_all_quests():
    url = "https://zealy.io/cw/mameinu/questboard"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=25)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        quests = set()
        
        for tag in soup.find_all(['h1','h2','h3','h4','div','span','a','p','strong']):
            text = tag.get_text(strip=True)
            if len(text) > 12 and len(text) < 150:
                if any(skip in text for skip in ["All Outline", "Your privacy", "Cookie", "Outline", "0 /"]):
                    continue
                if any(k in text for k in ["Daily", "Raid", "Mame", "Follow", "Visit", "Spread", "Connect", "Capsule", "Timeline"]):
                    quests.add(text)
        
        return sorted(list(quests))[:30]
        
    except Exception as e:
        print(f"Lỗi quét: {e}")
        return []

async def send_all_quests():
    await bot.send_message(CHAT_ID, "🔍 Đang quét Questboard...")
    quests = get_all_quests()
    
    if not quests:
        await bot.send_message(CHAT_ID, "❌ Không lấy được quest. Thử lại sau.")
        return
    
    header = f"""📋 **TẤT CẢ NHIỆM VỤ HIỆN TẠI - MAME INU**
({len(quests)} quest)

"""
    message = header
    for i, q in enumerate(quests, 1):
        message += f"**{i}.** {q}\n\n"
        if len(message) > 3500 or i % 10 == 0:
            await bot.send_message(CHAT_ID, message, parse_mode="Markdown", disable_web_page_preview=True)
            message = ""
            await asyncio
