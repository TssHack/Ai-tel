import asyncio
import aiohttp
from telethon import TelegramClient, events

# اطلاعات ورود به حساب کاربری
api_id = 17064702  # جایگزین شود
api_hash = "f65880b9eededbee85346f874819bbc5"  # جایگزین شود
session_name = "my_ai_bot"

client = TelegramClient(session_name, api_id, api_hash)

# تابع برای ارسال درخواست به API
async def fetch_api(url, params=None, method="GET", json_data=None, headers=None):
    try:
        async with aiohttp.ClientSession() as session:
            if method == "GET":
                async with session.get(url, params=params) as response:
                    return await response.json()
            elif method == "POST":
                async with session.post(url, json=json_data, headers=headers) as response:
                    return await response.text()
    except aiohttp.ClientError as e:
        return f"🚫 خطا در اتصال به سرور: {str(e)}"
    except Exception as e:
        return f"⚠️ مشکلی رخ داده است: {str(e)}"

# تابع برای API نوع "gpt"
async def chat_with_gpt(query):
    url = "https://open.wiki-api.ir/apis-1/ChatGPT"
    response = await fetch_api(url, params={"q": query})
    return response.get("results", "❌ پاسخی از ChatGPT دریافت نشد.") if isinstance(response, dict) else response

# تابع برای API نوع "pro"
async def chat_with_pro(query):
    url = "https://open.wiki-api.ir/apis-1/ChatGPT-4o"
    response = await fetch_api(url, params={"q": query})
    return response.get("results", "❌ پاسخی از ChatGPT-4o دریافت نشد.") if isinstance(response, dict) else response

# تابع برای API نوع "ai"
async def chat_with_ai(query, chat_id):
    try:
        url = "https://api.binjie.fun/api/generateStream"
        headers = {
            "authority": "api.binjie.fun",
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "origin": "https://chat18.aichatos.xyz",
            "referer": "https://chat18.aichatos.xyz/",
            "user-agent": "Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
            "Content-Type": "application/json"
        }
        data = {
            "prompt": query,
            "userId": str(chat_id),
            "network": True,
            "system": "",
            "withoutContext": False,
            "stream": False
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                response_text = await response.text()
                return response_text.strip() if response_text else "🚫 پاسخی از سرور دریافت نشد."

    except aiohttp.ClientError as e:
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

    # بررسی نوع API
    api_type = "default"
    query = message  # مقدار پیش‌فرض پیام

    if message.startswith("pro ") or message.endswith(" pro"):
        api_type = "pro"
        query = message.replace("pro", "").strip()
    elif message.startswith("gpt ") or message.endswith(" gpt"):
        api_type = "gpt"
        query = message.replace("gpt", "").strip()

    # در گروه‌ها فقط اگر پیام شامل "ai"، "pro" یا "gpt" باشد پردازش انجام شود
    if event.is_group and not any(word in message for word in ["ai", "pro", "gpt"]):
        return

    async with client.action(chat_id, "typing"):
        if api_type == "pro":
            response = await chat_with_pro(query)
        elif api_type == "gpt":
            response = await chat_with_gpt(query)
        else:
            response = await chat_with_ai(query, chat_id)

        # بررسی اینکه پاسخ نباید خالی باشد
        if not response.strip():
            response = "⚠️ پاسخی دریافت نشد. لطفاً دوباره امتحان کنید."

        await event.reply(response)

# اجرای ربات
async def main():
    await client.start()
    print("🤖 ربات فعال شد!")
    await client.run_until_disconnected()

asyncio.run(main())
