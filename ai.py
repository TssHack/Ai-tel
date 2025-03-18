import asyncio
import requests
from telethon import TelegramClient, events
import time

# اطلاعات ورود به حساب کاربری
api_id = 17064702  # جایگزین شود
api_hash = "f65880b9eededbee85346f874819bbc5"  # جایگزین شود
session_name = "my_ai_bot"

client = TelegramClient(session_name, api_id, api_hash)

# تابع برای ارسال درخواست به API نوع "gpt"
def chat_with_gpt(query):
    try:
        response = requests.get(f"https://open.wiki-api.ir/apis-1/ChatGPT?q={user_message}")
        data = response.json()
        return data.get("results", "پاسخی از ChatGPT دریافت نشد.")
    except:
        return "مشکلی در ارتباط با سرور ChatGPT رخ داد."
# تابع برای ارسال درخواست به API نوع "pro"
def chat_with_pro(query):
    try:
        response = requests.get(f"https://open.wiki-api.ir/apis-1/ChatGPT-4o?q={user_message}")
        data = response.json()
        return data.get("results", "پاسخی از ChatGPT دریافت نشد.")
    except:
        return "مشکلی در ارتباط با سرور ChatGPT رخ داد."

# تابع برای ارسال درخواست به API نوع "ai" (پیش‌فرض)
def chat_with_ai_api(query, chat_id):
    try:
        url = "https://api.binjie.fun/api/generateStream"
        headers = {
            "authority": "api.binjie.fun",
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "origin": "https://chat18.aichatos.xyz",
            "referer": "https://chat18.aichatos.xyz/",
            "user-agent": "Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
            "Content-Type": "application/json"
        }
        data = {
            "prompt": query,
            "userId": str(chat_id),  # مقدار chat_id را به‌عنوان userId تنظیم کردیم
            "network": True,
            "system": "",
            "withoutContext": False,
            "stream": False
        }

        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.encoding = 'utf-8'
        response_text = response.text.strip()

        return response_text if response_text else "🚫 پاسخی از سرور دریافت نشد."

    except requests.exceptions.Timeout:
        return "⏳ زمان انتظار به پایان رسید. لطفاً دوباره تلاش کنید."
    except requests.exceptions.RequestException as e:
        return f"🚫 خطا در اتصال به سرور: {str(e)}"
    except Exception as e:
        return f"⚠️ مشکلی رخ داده است: {str(e)}"
# گوش دادن به پیام‌ها
@client.on(events.NewMessage)
async def handle_message(event):
    chat_id = event.chat_id
    message = event.raw_text.strip().lower()

    # راهنما
    if message == "راهنما":
        help_text = (
            "📌 **راهنمای ربات:**\n"
            "1️⃣ برای استفاده از **ChatGPT-4o** ابتدا یا انتهای پیام خود `pro` قرار دهید.\n"
            "2️⃣ برای استفاده از **ChatGPT** ابتدا یا انتهای پیام خود `gpt` قرار دهید.\n"
            "3️⃣ در گروه‌ها فقط در صورتی که پیام شامل `ai`، `pro` یا `gpt` باشد پردازش می‌شود.\n"
            "✍ نویسنده: @abj0o"
        )
        await event.reply(help_text)
        return

    # تعیین نوع API بر اساس پیام
    api_type = "default"
    query = message  # مقدار پیش‌فرض پیام

    if message.startswith("pro ") or message.endswith(" pro"):
        api_type = "pro"
        query = message.replace("pro", "", 1).strip()
    elif message.startswith("gpt ") or message.endswith(" gpt"):
        api_type = "gpt"
        query = message.replace("gpt", "", 1).strip()

    # در گروه‌ها فقط اگر پیام شامل "ai"، "pro" یا "gpt" باشد پردازش انجام شود
    if event.is_group:
        if "ai" in message or "pro" in message or "gpt" in message:
            start_time = time.time()  # زمان شروع پردازش در گروه‌ها
            async with client.action(chat_id, "typing"):
                if api_type == "pro":
                    response = chat_with_pro(query, chat_id)
                elif api_type == "gpt":
                    response = chat_with_gpt(query, chat_id)
                else:
                    response = chat_with_ai(query, chat_id)
                await event.reply(response)
                typing_duration = time.time() - start_time
                print(f"زمان تایپینگ: {typing_duration:.2f} ثانیه")

    # در پیوی به تمام پیام‌ها پاسخ دهد
    elif event.is_private:
        start_time = time.time()  # زمان شروع پردازش در پیوی
        async with client.action(chat_id, "typing"):
            if api_type == "pro":
                response = chat_with_pro(query, chat_id)
            elif api_type == "gpt":
                response = chat_with_gpt(query, chat_id)
            else:
                response = chat_with_ai(query, chat_id)
            await event.reply(response)
            typing_duration = time.time() - start_time
            print(f"زمان تایپینگ: {typing_duration:.2f} ثانیه")

# اجرای ربات
async def main():
    await client.start()
    print("🤖 ربات فعال شد!")
    await client.run_until_disconnected()

asyncio.run(main())
