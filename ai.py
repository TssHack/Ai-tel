import asyncio
import aiohttp
from telethon import TelegramClient, events
from telethon import functions, types
from telethon.tl.functions.messages import SetTypingRequest
from telethon.tl.types import SendMessageTypingAction

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
        "prompt": query,  # ارسال query به‌روزرسانی‌شده
        "userId": str(user_id),
        "network": True,
        "system": "",
        "withoutContext": False,
        "stream": False
    }
    return await fetch_api(url, json_data=data, headers=headers)

async def download_soundcloud_audio(track_url):
    api_url = f"https://open.wiki-api.ir/apis-1/SoundcloudDownloader?url={track_url}"
    
    try:
        response = requests.get(api_url)
        if response.status_code != 200:
            return None, "⚠️ خطا در دریافت اطلاعات از API"
        
        data = response.json()
        if "results" not in data or "dlink" not in data["results"]:
            return None, "⚠️ لینک دانلود پیدا نشد"
        
        # اطلاعات موزیک
        audio_url = data["results"]["dlink"]
        name = data["results"].get("name", "نامشخص")
        artist = data["results"].get("artist", "نامشخص")
        thumb_url = data["results"].get("thumb", None)  # لینک کاور آهنگ
        
        # دانلود فایل
        filename = f"{name}.mp3"
        audio_response = requests.get(audio_url, stream=True)
        if audio_response.status_code == 200:
            with open(filename, "wb") as file:
                for chunk in audio_response.iter_content(chunk_size=1024):
                    file.write(chunk)
            return filename, name, artist, thumb_url
        else:
            return None, "⚠️ دانلود موزیک ناموفق بود"
    
    except Exception as e:
        return None, f"⚠️ خطا: {str(e)}"

async def search_soundcloud(query):
    api_url = f"https://open.wiki-api.ir/apis-1/SoundcloudeSearch/?q={query}"
    
    try:
        response = requests.get(api_url)
        if response.status_code != 200:
            return None, "⚠️ خطا در دریافت اطلاعات از API"
        
        data = response.json()
        if "results" not in data or not data["results"]:
            return None, "⚠️ هیچ نتیجه‌ای پیدا نشد!"
        
        return data["results"][:5]  # فقط ۵ نتیجه اول را برمی‌گرداند
    
    except Exception as e:
        return None, f"⚠️ خطا: {str(e)}"

# گوش دادن به پیام‌ها
# گوش دادن به پیام‌ها


@client.on(events.NewMessage)
async def handle_message(event):
    chat_id = event.chat_id
    user_id = event.sender_id
    message = event.raw_text.strip()

    if "ehsan" in message:
        query = message.split("mo", 1)[1].strip()  # فقط متن بعد از "mo" پردازش شود

        if not query:
            await event.reply("⚠️ لطفاً بعد از 'ehsan' یک عبارت جستجو وارد کنید.")
            return

        async with client.action(chat_id, "typing"):
            await event.reply(f"🔍 در حال جستجو برای: **{query}**...")

            results = await search_soundcloud(query)

            if not results:
                await event.reply("🚫 نتیجه‌ای پیدا نشد!")
                return

            # ارسال هر کدام از ۵ نتیجه در یک پیام جداگانه
            for result in results:
                title = result.get("title", "بدون عنوان")
                link = result.get("link", "بدون لینک")
                img = result.get("img", None) if result.get("img") != "Not found" else None
                description = result.get("description", "بدون توضیحات")

                caption = f"🎵 **{title}**\n🔗 [لینک ساندکلاد]({link})\n📝 {description}"

                if img:
                    await client.send_file(chat_id, img, caption=caption)
                else:
                    await event.reply(caption)
                    
        return

    if "soundcloud.com" in message:
        async with client.action(chat_id, "record-audio"):
            await event.reply("🎵 در حال دانلود موزیک از ساندکلاد... لطفاً صبر کنید.")

            file_path, name, artist, thumb_url = await download_soundcloud_audio(message)

            if file_path:
                caption = f"🎶 **نام آهنگ:** {name}\n👤 **هنرمند:** {artist}\n🔗 [لینک اصلی]({message})"
                
                # **فعال کردن اکشن "در حال آپلود" هنگام ارسال موزیک**
                async with client.action(chat_id, "upload_audio"):
                    if thumb_url:
                        await client.send_file(chat_id, file_path, caption=caption, thumb=thumb_url)
                    else:
                        await client.send_file(chat_id, file_path, caption=caption)

                await event.reply("✅ موزیک ارسال شد!")
            else:
                await event.reply("🚫 دانلود موزیک با مشکل مواجه شد.")
        return

    # اگر فرستنده پیام کاربر موردنظر باشد، ری‌اکت 💔 بفرستد
    #if user_id == 5718655519:
        # ارسال واکنش به پیام
        #await client(functions.messages.SendReactionRequest(
            #peer=event.chat_id,
            #msg_id=event.message.id,
            #reaction=[types.ReactionEmoji(emoticon='💔')]  # ایموجی واکنش
        #))

    # from telethon import functions, typesبررسی اینکه پیام شامل "ai" باشد
    if "ai" not in message.lower():
        return

    # حذف "ai" از پیام (فقط اولین مورد)
    cleaned_message = message.replace("ai", "", 1).strip()

    # بررسی اینکه پس از حذف "ai"، پیام هنوز دارای محتوا باشد
    if not cleaned_message:
        return

    try:
        async with client.action(chat_id, "typing"):
            response = await chat_with_ai(cleaned_message, user_id)

            # بررسی اینکه پاسخ نباید خالی باشد
            if not response.strip():
                response = "⚠️ پاسخی دریافت نشد. لطفاً دوباره امتحان کنید."

            await event.reply(response)
    except ValueError:
        pass

# اجرای ربات
async def main():
    await client.start()
    print("🤖 ربات فعال شد!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
