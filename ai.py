import asyncio
import requests
from telethon import TelegramClient, events

# اطلاعات ورود به حساب کاربری
api_id = 17064702  # جایگزین شود
api_hash = "f65880b9eededbee85346f874819bbc5"  # جایگزین شود
session_name = "my_ai_bot"

client = TelegramClient(session_name, api_id, api_hash)

# تابع برای ارسال درخواست به API هوش مصنوعی
def chat_with_ai_api(query, user_id):
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
            "userId": str(user_id),
            "network": True,
            "system": "",
            "withoutContext": False,
            "stream": False
        }

        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.encoding = 'utf-8'  # دیکد کردن متن
        response_text = response.text.strip()  # حذف فاصله‌های اضافی

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
    sender = await event.get_sender()
    user_id = sender.id
    message = event.raw_text.strip()

    # در گروه‌ها فقط اگر `ai` در **ابتدا یا انتهای پیام** باشد
    if event.is_group and (message.lower().startswith("ai") or message.lower().endswith("ai")):
        query = message.replace("ai", "", 1).strip()  # حذف اولین مورد از "ai"
        if query:
            async with client.action(chat_id, "typing"):  # نمایش اکشن تایپینگ
                await asyncio.sleep(1)  # تأخیر طبیعی‌تر
                response = chat_with_ai_api(query, user_id)
                await event.reply(response)
    
    # در پیوی به تمام پیام‌ها پاسخ دهد
    elif event.is_private:
        async with client.action(chat_id, "typing"):  # نمایش اکشن تایپینگ
            await asyncio.sleep(1)  # تأخیر طبیعی‌تر
            response = chat_with_ai_api(message, user_id)
            await event.reply(response)

# اجرای ربات
async def main():
    await client.start()
    print("🤖 ربات فعال شد!")
    await client.run_until_disconnected()

asyncio.run(main())
