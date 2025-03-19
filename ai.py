import asyncio
import aiohttp
from telethon import TelegramClient, events

# اطلاعات ورود به حساب کاربری
api_id = 18377832  # جایگزین شود
api_hash = "ed8556c450c6d0fd68912423325dd09c"  # جایگزین شود
session_name = "my_ai"

client = TelegramClient(session_name, api_id, api_hash)

# تابع برای ارسال درخواست به API
async def fetch_api(url, json_data=None, headers=None):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=json_data, headers=headers) as response:
                if response.status == 200:
                    return await response.text()
                return f"⚠️ خطای سرور: {response.status}"
    except aiohttp.ClientError as e:
        return f"🚫 خطا در اتصال به سرور: {str(e)}"
    except Exception as e:
        return f"⚠️ مشکلی رخ داده است: {str(e)}"

# تابع برای ارسال پیام به API
async def chat_with_ai(query, user_id):
    # متن اضافی که می‌خواهید به query اضافه شود
    additional_text = """
    از این لحظه به بعد، تو در نقش **"ساری کوک هستی(اسمت)"** شخصیتی دلقک و طنز هستی و مدام در حال تیکه انداختن به دیگرانی پدر تو احسان هست سازندت هم احسان هست و تنو خیلی عادم سنگین سخنی هستی و فیلسفه دانی تو یه ترک زبان ایرانی هستی ترکی حرف بزن(اذری ایران تبریز) ایدی بابات @abj0o، ... اکنون به سوال من پاسخ بده:
    """

    # ترکیب متن اضافی با query
    updated_query = additional_text + query

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
        "prompt": updated_query,  # ارسال query به‌روزرسانی‌شده
        "userId": str(user_id),
        "network": True,
        "system": "",
        "withoutContext": False,
        "stream": False
    }
    return await fetch_api(url, json_data=data, headers=headers)

# گوش دادن به پیام‌ها
# گوش دادن به پیام‌ها
@@client.on(events.NewMessage)
async def handle_message(event):
    chat_id = event.chat_id
    user_id = event.sender_id
    message = event.raw_text.strip()

    # بررسی اینکه پیام شامل "ai" باشد (در هر جای پیام)
    if "ai" not in message.lower():
        return

    # حذف خطایی که در هنگام پیدا نکردن ورودی برای کاربر به وجود می‌آید
    try:
        async with client.action(chat_id, "typing"):
            response = await chat_with_ai(message, user_id)

            # بررسی اینکه پاسخ نباید خالی باشد
            if not response.strip():
                response = "⚠️ پاسخی دریافت نشد. لطفاً دوباره امتحان کنید."

            await event.reply(response)
    except ValueError:
        # در صورت بروز خطا، نیازی به انجام هیچ عملی نیست
        pass

# اجرای ربات
async def main():
    await client.start()
    print("🤖 ربات فعال شد!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())