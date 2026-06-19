import asyncio
import time
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
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
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://zealy.io/cw/mameinu/questboard")
        
        time.sleep(10)  # Chờ Zealy load đầy đủ JavaScript
        
        quests = []
        elements = driver.find_elements("xpath", "//*[contains(text(), 'Daily') or contains(text(), 'Raid') or contains(text(), 'Mame') or contains(@class, 'quest')]")
        
        for el in elements:
            text = el.text.strip()
            if len(text) > 15 and text not in quests:
                if any(k in text for k in ["Daily", "Raid", "Mame", "Follow", "Visit", "Spread", "Connect", "Capsule", "Timeline"]):
                    quests.append(text)
        
        driver.quit()
        return quests[:30]
        
    except Exception as e:
        print(f"Lỗi Selenium: {e}")
        return []
    finally:
        try:
            driver.quit()
        except:
            pass

async def send_all_quests():
    await bot.send_message(CHAT_ID, "🔍 Đang quét Questboard (mất 8-12 giây)...")
    quests = get_all_quests()
    
    if not quests:
        await bot.send_message(CHAT_ID, "❌ Không lấy được quest. Thử lại sau.")
        return
    
    header = f"""📋 **TẤT CẢ NHIỆM VỤ - MAME INU**
({len(quests)} quest)

"""
    message = header
    for i, q in enumerate(quests, 1):
        message += f"**{i}.** {q}\n\n"
        if len(message) > 3500 or i % 10 == 0:
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
    await message.answer("✅ Bot Mame Inu Quest đang chạy!\n/quêtes để xem tất cả nhiệm vụ.")

@dp.message(Command("quests"))
async def quests_command(message: types.Message):
    await send_all_quests()

async def scheduler():
    print("🚀 Bot Selenium khởi động...")
    await check_new_quests()
    while True:
        await asyncio.sleep(CHECK_INTERVAL)
        await check_new_quests()

async def main():
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
       
