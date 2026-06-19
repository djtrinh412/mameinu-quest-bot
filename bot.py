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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=25)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        quests = set()  # Dùng set để tránh trùng
        
        # Tìm tất cả các element có thể chứa tên quest
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'div', 'span', 'a', 'p', 'strong']):
            text = tag.get_text(strip=True)
            if len(text) > 12 and len(text) < 150:
                # Loại text rác
                if any(skip in text for skip in ["All Outline", "Your privacy", "Cookie", "Outline", "0 /", "Join the community"]):
                    continue
                if any(k in text for k in ["Daily", "Raid", "Mame", "Follow", "Visit", "Spread", "Connect", "Capsule", "Timeline"]):
                    quests.add(text)
        
        return sorted(list(quests))[:30]
        
    except Exception as e:
        print(f"Lỗi quét: {e}")
        return []

async def send_all_quests():
    await bot.send_message(CHAT_ID, "🔍 Đang quét Questboard (mất 5-8 giây)...")
    quests = get_all_quests()
    
    if not quests:
        await bot.send_message(CHAT_ID, "❌ Hiện tại không lấy được quest. Thử lại sau 1 phút.")
        return
    
    header = f"""📋 **TẤT CẢ NHIỆM VỤ HIỆN TẠI - MAME INU**
({len(quests)} quest)

"""
    message = header
    for i, q in enumerate(quests, 1):
        message += f"**{i}.** {q}\n\n"
        if len(message) > 3800 or i % 10 == 0:
            await bot.send_message(CHAT_ID, message, parse_mode="Markdown", disable_web_page_preview=True)
            message = ""
            await asyncio.sleep(1)
    
    if message:
        await bot.send_message(CHAT_ID, message, parse_mode="Markdown")
    
    await bot.send_message(CHAT_ID, "🔗 [Mở Questboard đầy đủ](https://zealy.io/cw/mameinu/questboard)", parse_mode="Markdown")

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
    await message.answer("✅ Bot đang chạy!\n/quêtes để xem tất
