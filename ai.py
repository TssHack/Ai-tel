import aiohttp
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SetTypingRequest
from telethon.tl.types import SendMessageTypingAction

# اطلاعات اکانت تلگرام (از my.telegram.org بگیرید)
api_id = 18377832  # 🔹 API ID خود را اینجا قرار دهید
api_hash = "ed8556c450c6d0fd68912423325dd09c"  # 🔹 API Hash خود را اینجا قرار دهید
session_name = "my_ai"  # 🔹 نام فایل سشن

# ایجاد کلاینت تلتون
client = TelegramClient(session_name, api_id, api_hash)

async def fetch_api(url, json_data=None, headers=None):
    """ ارسال درخواست به API و دریافت پاسخ """
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

async def chat_with_ai(query, user_id):
    """ ارسال پیام به API هوش مصنوعی و دریافت پاسخ """
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
        "userId": str(user_id),
        "network": True,
        "withoutContext": False,
        "stream": False
    }
    return await fetch_api(url, json_data=data, headers=headers)

@client.on(events.NewMessage)
async def handler(event):
    """ بررسی پیام‌ها و پاسخ‌دهی در صورت وجود 'ai' در متن """
    if "ai" in event.raw_text.lower():
        chat_id = event.chat_id
        user_id = event.sender_id
        message_text = event.raw_text

        # نمایش "در حال تایپ..."
        async with client.action(chat_id, "typing"):
            response = await chat_with_ai(message_text, event.sender_id)

        # ارسال پاسخ
        await event.reply(response)

# اجرای کلاینت
async def main():
    async with client:
        print("✅ ربات فعال شد!")
        await client.run_until_disconnected()

asyncio.run(main())