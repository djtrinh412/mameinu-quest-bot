import asyncio
import time
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("✅ Bot Mame Inu đang chạy ổn.")

@dp.message(Command("quests"))
async def quests(message: types.Message):
    msg = f"""📋 **MAME INU QUESTS**

🔗 Truy cập tất cả nhiệm vụ tại đây:
https://zealy.io/cw/mameinu/questboard

⏰ Cập nhật lúc: {time.strftime('%H:%M %d/%m/%Y')}
"""
    await message.answer(msg, disable_web_page_preview=True)

async def main():
    print("🚀 Bot started successfully")
    try:
        await bot.send_message(CHAT_ID, "✅ Bot Mame Inu Quest đã online!")
    except:
        pass
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
