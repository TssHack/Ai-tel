import asyncio
import requests
from telethon import TelegramClient, events

# اطلاعات ورود به حساب کاربری
api_id = 17064702  # جایگزین شود
api_hash = "f65880b9eededbee85346f874819bbc5"  # جایگزین شود
session_name = "my_ai_bot"

client = TelegramClient(session_name, api_id, api_hash)

# تابع برای ارسال درخواست به API
def chat_with_ai_api(query, chat_id, api_type="default"):
    try:
        # تعیین URL مناسب بر اساس نوع درخواست
        if api_type == "pro":
            url = f"https://open.wiki-api.ir/apis-1/ChatGPT-4o?q={query}"
        elif api_type == "gpt":
            url = f"https://open.wiki-api.ir/apis-1/ChatGPT?q={query}"
        else:
            url = "https://api.binjie.fun/api/generateStream"

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "user-agent": "Mozilla/5.0"
        }

        # ارسال درخواست GET برای APIهای ویکی  
        if api_type in ["pro", "gpt"]:
            response = requests.get(url, headers=headers, timeout=10)
        else:
            data = {
                "prompt": query,
                "userId": str(chat_id),
                "network": True,
                "system": "",
                "withoutContext": False,
                "stream": False
            }
            response = requests.post(url, headers=headers, json=data, timeout=10)

        response.encoding = 'utf-8'
        
        # بررسی اینکه آیا پاسخ خالی است
        if not response.text.strip():
            return "🚫 پاسخ سرور خالی است. لطفاً بعداً تلاش کنید."

        try:
            response_json = response.json()
        except requests.exceptions.JSONDecodeError:
            return f"⚠️ پاسخ نامعتبر از سرور دریافت شد:\n\n{response.text[:500]}"

        if response_json.get("status"):
            return response_json.get("results", "🚫 پاسخی از سرور دریافت نشد.")
        return "🚫 پاسخی از سرور دریافت نشد."

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
            async with client.action(chat_id, "typing"):
                await asyncio.sleep(1)
                response = chat_with_ai_api(query, chat_id, api_type)
                await event.reply(response)
    # در پیوی به تمام پیام‌ها پاسخ دهد
    elif event.is_private:
        async with client.action(chat_id, "typing"):
            await asyncio.sleep(1)
            response = chat_with_ai_api(query, chat_id, api_type)
            await event.reply(response)

# اجرای ربات
async def main():
    await client.start()
    print("🤖 ربات فعال شد!")
    await client.run_until_disconnected()

asyncio.run(main())
