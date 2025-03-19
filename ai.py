import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import aiohttp

# اطلاعات ورود به حساب شخصی
api_id = 18377832  # مقدار صحیح را جایگزین کنید
api_hash = "ed8556c450c6d0fd68912423325dd09c"
session_name = "my_ai"

app = Client(session_name, api_id=api_id, api_hash=api_hash)

# تابع دریافت اطلاعات از API
async def fetch_api(url, json_data=None, headers=None):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=json_data, headers=headers) as response:
                print(f"🔍 وضعیت درخواست به API: {response.status}")
                if response.status == 200:
                    return await response.text()
                return f"⚠️ خطای سرور: {response.status}"
    except aiohttp.ClientError as e:
        return f"🚫 خطا در اتصال به سرور: {str(e)}"
    except Exception as e:
        return f"⚠️ مشکلی رخ داده است: {str(e)}"

# تابع ارسال درخواست به AI
async def chat_with_ai(query, user_id):
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
    response = await fetch_api(url, json_data=data, headers=headers)
    print("📜 پاسخ دریافتی از AI:", response)
    return response

# تابع تبدیل متن به فونت‌های مختلف
async def convert_to_fonts(text):
    font_url = f"https://api.pamickweb.ir/API/FontEn.php?Text={text}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(font_url) as response:
                print(f"🔍 وضعیت درخواست فونت: {response.status}")
                if response.status == 200:
                    fonts = await response.text()
                    fonts_list = fonts.strip().split("\n")
                    return "\n".join([f"`{font}`" for font in fonts_list[:10]])  # فقط ۱۰ فونت اول را ارسال می‌کنیم
                else:
                    return "❌ خطا در دریافت فونت‌ها از سرور."
    except Exception as e:
        return f"⚠️ خطای اتصال: {str(e)}"

# بررسی پیام‌های ورودی
@app.on_message(filters.text)
async def handle_message(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text.strip().lower()

    print(f"📩 پیام جدید از {user_id}: {text}")

    if "ai" in text:
        print("✅ پیام شامل 'ai' است، پردازش می‌شود...")
        await client.send_chat_action(chat_id, "typing")
        response = await chat_with_ai(text, user_id)
        if not response.strip():
            response = "⚠️ پاسخی دریافت نشد. لطفاً دوباره امتحان کنید."
        await message.reply(response)
        return

    if text.startswith("font "):
        input_text = text[5:]
        print(f"🎨 درخواست تبدیل فونت دریافت شد: {input_text}")
        await client.send_chat_action(chat_id, "typing")
        response = await convert_to_fonts(input_text)
        await message.reply(response)
        return

# اجرای برنامه
async def main():
    async with app:
        print("🤖 ربات با اکانت شخصی فعال شد!")
        await app.start()
        await app.send_message("me", "Hi!")
        await app.stop()

    asyncio.run(main())