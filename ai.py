import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import aiohttp

# اطلاعات ورود به حساب شخصی
api_id = 18377832  # مقدار صحیح را جایگزین کن
api_hash = "ed8556c450c6d0fd68912423325dd09c"
session_name = "my_ai"

app = Client(session_name, api_id, api_hash)


# تابع دریافت اطلاعات از API
async def fetch_api(url, json_data=None, headers=None):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=json_data, headers=headers) as response:
                response.raise_for_status()  # بررسی وضعیت درخواست
                return await response.text()
    except aiohttp.ClientResponseError as e:
        return f"⚠️ خطای سرور: {e.status} - {e.message}"
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
        "Content-Type": "application/json",
    }
    data = {
        "prompt": query,
        "userId": str(user_id),
        "network": True,
        "system": "",
        "withoutContext": False,
        "stream": False,
    }
    return await fetch_api(url, json_data=data, headers=headers)


# تابع تبدیل متن به فونت‌های مختلف
async def convert_to_fonts(text):
    font_url = f"https://api.pamickweb.ir/API/FontEn.php?Text={text}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(font_url) as response:
                response.raise_for_status()
                fonts = await response.text()
                fonts_list = fonts.strip().split("\n")
                return "\n".join([f"`{font}`" for font in fonts_list[:10]])  # فقط ۱۰ فونت اول را ارسال می‌کنیم
    except aiohttp.ClientResponseError as e:
        return f"⚠️ خطای سرور: {e.status} - {e.message}"
    except aiohttp.ClientError as e:
        return f"🚫 خطا در اتصال به سرور: {str(e)}"
    except Exception as e:
        return f"⚠️ مشکلی رخ داده است: {str(e)}"


# بررسی پیام‌های گروهی
@app.on_message(filters.text & filters.group)
async def handle_message(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text.strip().lower()

    # فقط پیام‌هایی که شامل "ai" هستند پردازش شوند
    if "ai" in text:
        await message.chat.send_chat_action("typing")
        response = await chat_with_ai(text, user_id)
        if not response.strip():
            response = "⚠️ پاسخی دریافت نشد. لطفاً دوباره امتحان کنید."
        await message.reply(response)
        return

    # اگر پیام با "font" شروع شود، متن را به فونت‌های مختلف تبدیل کن
    if text.startswith("font "):
        input_text = text[5:]  # حذف "font " از ابتدای متن
        await message.chat.send_chat_action("typing")
        response = await convert_to_fonts(input_text)
        await message.reply(response)
        return


# اجرای برنامه
if __name__ == "__main__":
    print("🤖 ربات در حال اجراست...")
    app.run()