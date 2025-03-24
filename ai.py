import asyncio
import re
import aiohttp
import os
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji

# اطلاعات ورود به حساب تلگرام
api_id = 18377832  # جایگزین شود
api_hash = "ed8556c450c6d0fd68912423325dd09c"  # جایگزین شود
session_name = "my_ai"

client = TelegramClient(session_name, api_id, api_hash)


async def process_link(url):
    api_url = f"https://pp-don.onrender.com/?url={url}"  # آدرس API جدید
    max_retries = 3  # تعداد دفعات تلاش مجدد

    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    data = await response.json()
            
            if data.get("code") == 200 and "data" in data:
                video_data = data["data"]
                title = video_data.get("title", "بدون عنوان")
                image = video_data.get("image", "")
                
                # استخراج کیفیت‌ها به ترتیب
                qualities = video_data.get("video_quality", [])
                sorted_qualities = sorted(qualities, key=lambda q: q['type'])

                result = f"🎥 **{title}**\n\n🔗 **لینک‌ها:**\n"
                
                # نمایش لینک‌ها با کیفیت‌های مختلف
                quality_links = {
                    "240p": None,
                    "480p": None,
                    "720p": None,
                    "1080p": None
                }

                # مرتب کردن کیفیت‌ها بر اساس اولویت 240p, 480p, 720p, 1080p
                for quality in sorted_qualities:
                    if quality['type'] == "426x240" and not quality_links["240p"]:
                        quality_links["240p"] = f"🔹 **240p**: {quality['url']}"
                    elif quality['type'] == "854x480" and not quality_links["480p"]:
                        quality_links["480p"] = f"🔹 **480p**: {quality['url']}"
                    elif quality['type'] == "1280x720" and not quality_links["720p"]:
                        quality_links["720p"] = f"🔹 **720p**: {quality['url']}"
                    elif quality['type'] == "1920x1080" and not quality_links["1080p"]:
                        quality_links["1080p"] = f"🔹 **1080p**: {quality['url']}"

                for quality, link in quality_links.items():
                    if link:
                        result += f"{link}\n"
                    else:
                        result += f"❌ لینک با کیفیت {quality} موجود نیست.\n"

                return result, image
            elif data.get("code") == 600:
                # خطای 600: "Something is wrong, please try again!"
                if attempt < max_retries - 1:
                    continue  # تلاش مجدد
                else:
                    return "❌ پردازش لینک با خطا مواجه شد. لطفاً دوباره تلاش کنید.", None
            else:
                return "❌ پردازش لینک با خطا مواجه شد.", None
        except Exception as e:
            if attempt < max_retries - 1:
                continue  # تلاش مجدد
            else:
                return f"❌ خطا در پردازش: {str(e)}", None

# جستجو در دیوار
async def search_divar(query, city="tabriz"):
    api_url = f"https://open.wiki-api.ir/apis-1/SearchDivar?city={city}&q={query}"

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status != 200:
                return None, "⚠️ خطا در دریافت اطلاعات از دیوار."

            data = await response.json()

            if "status" in data and data["status"] == True:
                results = data["results"][:20]  # نمایش ۱۰ نتیجه اول
                return results, None
            return None, "⚠️ هیچ نتیجه‌ای یافت نشد!"

# تابع درخواست به API
async def fetch_api(url, json_data=None, headers=None):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=json_data, headers=headers) as response:
                return await response.text() if response.status == 200 else f"⚠️ خطای سرور: {response.status}"
    except Exception as e:
        return f"🚫 خطا در اتصال: {str(e)}"

# چت با هوش مصنوعی
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

# دانلود موزیک از SoundCloud
async def download_soundcloud_audio(track_url):
    api_url = f"https://open.wiki-api.ir/apis-1/SoundcloudDownloader?url={track_url}"

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status != 200:
                return None, None, None, None  # اصلاح مقدار بازگشتی

            data = await response.json()
            if "results" not in data or "dlink" not in data["results"]:
                return None, None, None, None  # اصلاح مقدار بازگشتی

            audio_url = data["results"]["dlink"]
            name = data["results"].get("name", "نامشخص")
            artist = data["results"].get("artist", "نامشخص")
            thumb_url = data["results"].get("thumb", None)

            # دانلود فایل
            filename = f"{name}.mp3"
            async with session.get(audio_url) as audio_response:
                if audio_response.status == 200:
                    with open(filename, "wb") as file:
                        file.write(await audio_response.read())
                    return filename, name, artist, thumb_url
                return None, None, None, None  # اصلاح مقدار بازگشتی

# جستجو در SoundCloud
async def search_soundcloud(query):
    api_url = f"https://open.wiki-api.ir/apis-1/SoundcloudeSearch/?q={query}"

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status != 200:
                return None, "⚠️ خطا در دریافت اطلاعات"

            data = await response.json()
            return data["results"][:5] if "results" in data and data["results"] else None, "⚠️ هیچ نتیجه‌ای یافت نشد!"

# گوش دادن به پیام‌ها
@client.on(events.NewMessage)
async def handle_message(event):
    chat_id = event.chat_id
    user_id = event.sender_id
    message = event.raw_text.strip()

    # جستجو در SoundCloud
    if message.lower().startswith("ehsan "):
        query = message[6:].strip()
        if not query:
            await event.reply("⚠️ لطفاً بعد از 'ehsan' عبارت جستجو وارد کنید.")
            return

        async with client.action(chat_id, "typing"):
            await event.reply(f"🔍 در حال جستجو برای: **{query}**...")

            results, error = await search_soundcloud(query)
            if not results:
                await event.reply(error)
                return

            for result in results:
                title = result.get("title", "بدون عنوان")
                link = result.get("link", "بدون لینک")
                img = result.get("img", None) if result.get("img") != "Not found" else None
                description = result.get("description", "بدون توضیحات")

                caption = f"🎵 **{title}**\n🔗 [لینک ساندکلاد]({link})"

                # محدود کردن متن کپشن به 1000 کاراکتر برای جلوگیری از خطای طولانی بودن کپشن
                caption = caption[:950] + "..." if len(caption) > 1000 else caption

                if img:
                    await client.send_file(chat_id, img, caption=caption)
                else:
                    await event.reply(caption)
        return

    # دانلود آهنگ از SoundCloud
    if "soundcloud.com" in message:
        async with client.action(chat_id, "record-audio"):
            await event.reply("🎵 در حال دانلود موزیک... لطفاً صبر کنید.")

            file_path, _, _, _ = await download_soundcloud_audio(message)  # فقط فایل موزیک را دریافت کن

            if not file_path:
                await event.reply("🚫 دانلود موزیک با مشکل مواجه شد.")
                return

    # ارسال فایل بدون هیچ متنی
            async with client.action(chat_id, "document"):
                await client.send_file(chat_id, file_path)

    # حذف فایل پس از ارسال
            if os.path.exists(file_path):
                os.remove(file_path)

    if re.search(r"https://www.pornhub\.com/view_video\.php\?viewkey=\S+", message):
        url = re.search(r"https://www.pornhub\.com/view_video\.php\?viewkey=\S+", message).group(0)
        await event.reply("⏳ در حال پردازش لینک...")

        # پردازش لینک
        result, image = await process_link(url)

        # ارسال نتیجه به کاربر
        if image:
            await event.reply(result, file=image)
        else:
            await event.reply(result)

    # اضافه کردن سایر توابع یا پردازش‌های دیگر (اگر وجود داشته باشد)
    else:
        # پردازش سایر لینک‌ها یا پیام‌ها
        pass

    # ارسال پیام به هوش مصنوعی
    if "ai" in message.lower():
        cleaned_message = message.replace("ai", "", 1).strip()
        if not cleaned_message:
            return

        try:
            async with client.action(chat_id, "typing"):
                response = await chat_with_ai(cleaned_message, user_id)
                response = response.strip() if response and response.strip() else "⚠️ پاسخی دریافت نشد!"
                response = response[:950] + "..." if len(response) > 1000 else response  # محدود کردن متن خروجی
                await event.reply(response)
        except Exception as e:
            await event.reply(f"🚫 خطا در پردازش پیام: {str(e)}")
        return

    # جستجو در دیوار
    if message.lower().startswith("divar "):
        query = message[6:].strip()
        if not query:
            await event.reply("⚠️ لطفاً بعد از 'divar' عبارت جستجو وارد کنید.")
            return

        async with client.action(chat_id, "typing"):
            await event.reply(f"🔍 در حال جستجو برای: **{query}** در دیوار...")

            results, error = await search_divar(query)
            if not results:
                await event.reply(error)
                return

            for result in results:
                title = result.get("title", "بدون عنوان")
                description = result.get("description", "بدون توضیحات")
                price = result.get("price", "بدون قیمت")
                date = result.get("date", "بدون تاریخ")
                link = result.get("link", "بدون لینک")
                image = result.get("image", None)

                # قالب‌بندی پیام
                caption = f"📌 *{title}*\n" \
                          f"📜 {description}\n" \
                          f"💰 *قیمت:* {price}\n" \
                          f"📍 *تاریخ:* {date}\n" \
                          f"🔗 [مشاهده آگهی]({link})"

                # محدود کردن طول پیام
                caption = caption[:950] + "..." if len(caption) > 1000 else caption

                # ارسال عکس یا پیام با لینک پیش‌نمایش
                if image and image.startswith("http"):
                    await client.send_file(chat_id, image, caption=caption, reply_to=event.message.id)
                else:
                    await event.reply(caption, link_preview=True, reply_to=event.message.id)

        return
# اجرای ربات
async def main():
    await client.start()
    print("🤖 ربات فعال شد!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
