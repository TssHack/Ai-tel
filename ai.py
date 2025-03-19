import asyncio
import aiohttp
from pyrogram import Client, filters

# اطلاعات ورود به حساب کاربری
api_id = 18377832  # جایگزین شود
api_hash = "ed8556c450c6d0fd68912423325dd09c"  # جایگزین شود
session_name = "my_ai"  # این مقدار می‌تواند نام فایل سشن باشد

# ساخت کلاینت Pyrogram
app = Client(session_name, api_id, api_hash)

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

# تابع برای ارسال پیام به API هوش مصنوعی
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
        "system": "",
        "withoutContext": False,
        "stream": False
    }
    return await fetch_api(url, json_data=data, headers=headers)

# تابع دریافت فونت‌های مختلف برای متن انگلیسی
async def convert_to_fonts(text):
    font_url = f"https://api.pamickweb.ir/API/FontEn.php?Text={text}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(font_url, timeout=5) as response:
                if response.status == 200:
                    fonts = await response.text()
                    fonts_list = fonts.split("\n")  # جدا کردن فونت‌ها
                    return "\n".join([f"`{font}`" for font in fonts_list])  # نمایش فونت‌ها به‌صورت کد
                else:
                    return "❌ خطا: نتوانستم فونت‌ها را دریافت کنم."
    
    except asyncio.TimeoutError:
        return "⏳ سرور پاسخگو نیست، لطفاً بعداً امتحان کنید."
    
    except aiohttp.ClientError as e:
        return f"⚠️ خطای اتصال: {e}"

# پردازش پیام‌های دریافتی
@app.on_message(filters.text & ~filters.private)
async def handle_message(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text.strip()

    # راهنما
    if text.lower() == "راهنما":
        help_text = (
            "📌 **راهنمای ربات:**\n"
            "🔹 در گروه‌ها فقط پیام‌هایی که شامل `ai` باشند پردازش می‌شوند.\n"
            "🔹 برای دریافت فونت‌های یک متن انگلیسی، ابتدای پیام خود `font` بنویسید.\n"
            "✍ نویسنده: @abj0o"
        )
        await message.reply(help_text)
        return

    # تبدیل متن به فونت‌های مختلف
    if text.lower().startswith("font "):
        query_text = text[5:].strip()
        if not query_text:
            await message.reply("❌ لطفاً یک متن انگلیسی بعد از `font` وارد کنید.")
            return
        
        async with app.send_chat_action(chat_id, "typing"):
            fonts = await convert_to_fonts(query_text)
            await message.reply(fonts)
        return

    # فقط پیام‌هایی که شامل "ai" باشند پردازش شوند
    if "ai" not in text.lower():
        return

    async with app.send_chat_action(chat_id, "typing"):
        response = await chat_with_ai(text, user_id)

        # بررسی اینکه پاسخ نباید خالی باشد
        if not response.strip():
            response = "⚠️ پاسخی دریافت نشد. لطفاً دوباره امتحان کنید."

        await message.reply(response)

# اجرای ربات
async def main():
    async with app:
        print("🤖 ربات فعال شد!")
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
