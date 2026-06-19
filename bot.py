import asyncio
import time
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

# ================== CONFIG ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
CHECK_INTERVAL = 60
# ===========================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

seen_quests = set()

def get_all_quests_selenium():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=options)
    quests = []
    
    try:
        driver.get("https://zealy.io/cw/mameinu/questboard")
        time.sleep(8)  # Chờ load JS
        
        # Lấy tất cả text
        elements = driver.find_elements("xpath", "//h3 | //h4 | //div[contains(@class,'quest')] | //span")
        
        for el in elements:
            text = el.text.strip()
            if len(text) > 12 and text not in quests:
                if any(k in text for k in ["Daily", "Raid", "Mame", "Follow", "Visit", "Spread", "Connect", "Capsule"]):
                    quests.append(text)
        
        return quests[:25]
        
    except Exception as e:
        print(f"Lỗi Selenium: {e}")
        return []
    finally:
        driver.quit()

async def send_all_quests():
    quests = get_all_quests_selenium()
    if not quests:
        await bot.send_message(CHAT_ID, "❌ Không lấy được quest (Zealy load chậm). Thử lại sau.")
        return
    
    header = f"📋 **TẤT CẢ NHIỆM VỤ - MAME INU** ({len(quests)} quest)\n\n"
    message = header
    for i, q in enumerate(quests, 1):
        message += f"**{i}.** {q}\n\n"
        if len(message) > 3500:
            await bot.send_message(CHAT_ID, message, parse_mode="Markdown")
            message = ""
            await asyncio.sleep(1)
    
    if message:
        await bot.send_message(CHAT_ID, message, parse_mode="Markdown")
    
    await bot.send_message(CHAT_ID, "🔗 [Questboard](https://zealy.io/cw/mameinu/questboard)")

# Các hàm còn lại giữ nguyên...
async def check_new_quests():
    global seen_quests
    quests = get_all_quests_selenium()
    new_quests = [q for q in quests if q not in seen_quests]
    for q in new_quests:
        seen_quests.add(q)
    if new_quests:
        for q in new_quests[:4]:
            msg = f"🚨 **QUEST MỚI** 🚨\n\n{q}\n\n🔗 [Tham gia](https://zealy.io/cw/mameinu/questboard)"
            await bot.send_message(CHAT_ID, msg, parse_mode="Markdown")

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("✅ Bot đang chạy!\n/quêtes để xem tất cả nhiệm vụ.")

@dp.message(Command("quests"))
async def quests_command(message: types.Message):
    await message.answer("🔍 Đang quét... (có thể mất 8-10 giây)")
    await send_all_quests()

async def scheduler():
    print("🚀 Bot khởi động với Selenium")
    await check_new_quests()
    while True:
        await asyncio.sleep(CHECK_INTERVAL)
        await check_new_quests()

async def main():
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
