FROM mcr.microsoft.com/playwright:v1.42.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Cài đặt trình duyệt cho Playwright
RUN playwright install chromium

COPY . .

CMD ["python", "bot.py"]
