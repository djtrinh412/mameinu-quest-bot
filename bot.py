import asyncio
import time
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import os

# ================== CONFIG ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
# ===========================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "✅ **Bot Mame Inu Quest** đã chạy thành công!\n\n"
        "Dùng lệnh `/quests` để xem Questboard."
    )

@dp.message(Command("quests"))
async def quests(message: types.Message):
    msg = f"""📋 **QUESTBOARD MAME INU**

🔗 [Nhấn vào đây xem tất cả nhiệm vụ hiện tại](https://zealy.io/cw/mameinu/questboard)

⏰ Cập nhật: {time.strftime('%H:%M %d/%m/%Y')}
"""
    await message.answer(msg, parse_mode="Markdown", disable_web_page_preview=True)

async def main():
    print("🚀 Bot Mame Inu Quest đã khởi động!")
    try:
        await bot.send_message(
            CHAT_ID, 
            "✅ **Bot đã online thành công!**\nGõ /quests để xem nhiệm vụ."
        )
    except:
        pass
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
