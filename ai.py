import asyncio
import re
import requests
import httpx
from datetime import datetime
import aiohttp
import os
from PIL import Image
from io import BytesIO
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji

# اطلاعات ورود به حساب تلگرام
api_id = 18377832  # جایگزین شود
api_hash = "ed8556c450c6d0fd68912423325dd09c"  # جایگزین شود
session_name = "my_ai"

client = TelegramClient(session_name, api_id, api_hash)

robot_status = True

licenses = [
    "Sl6ELFq-nUnpkAE-gCNZqJQ-2W8335T-1SAPzwG",
    "tmPiWoM-6FXRaLt-GwPgLVH-y6g6dHr-dUyLJi3",
    "0ZVxR67-y7Dd6zh-C2jLE21-kY50NYC-GNxiJod",
    "eLwm3cR-2XegSsv-9l9DCta-q4ng622-EeuAsSy",
    "ucGWVCM-S5nHEzi-bss0SdJ-WDwABuG-6YWzWU2",
    "GvrtzqZ-jK3MkEK-NRqhjW1-wvNqXUn-QrKsrDP",
    "5Ti1I4O-SXQ0kp1-qLcZ529-qQ1QgIR-i5QM7oV",
    "3Qk17MU-jc6fJ4g-XFLOCVy-EJlWSmc-c9nxR71",
    "ctorzhF-9vxEUIb-AqybTch-MCJe0Oh-SWx1G7d",
    "lZEcaGZ-5SeK0bS-N6urNSx-tc9WwZO-qJEkcsT",
    "Dg20ygp-6d46CtA-OqEZtv3-CRko2qE-oORjhN0",
    "QabJdKR-4VULYJ4-lOqS19N-FOANKGz-ZuysnYH"
]
current_index = 0

def get_estekhare():
    url = "https://stekhare.onrender.com/s"
    response = requests.get(url)
    try:
        data = response.json()
        if "url" in data:
            return data["url"]
    except Exception as e:
        print(f"JSON Decode Error: {e}")
    return None

# تابع دانلود و ذخیره تصویر با بازسازی فرمت صحیح
def download_image(img_url, filename="estekhare.jpg"):
    try:
        response = requests.get(img_url, stream=True)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            image = image.convert("RGB")  # تبدیل به RGB برای جلوگیری از مشکلات فرمت
            image.thumbnail((800, 800))  # کاهش اندازه تصویر به 800×800 پیکسل
            image.save(filename, format="JPEG", quality=85)  # ذخیره با کیفیت پایین‌تر
            return filename
    except Exception as e:
        print(f"Error downloading image: {e}")
    return None

def get_horoscope():
    url = "https://open.wiki-api.ir/apis-1/Horoscope/?key=Sl6ELFq-nUnpkAE-gCNZqJQ-2W8335T-1SAPzwG"
    response = requests.get(url)
    data = response.json()

    if data["detail"]["status"] == "success":
        horoscope = data["detail"]["data"]
        return horoscope
    return None

def download_image(img_url, filename="horoscope_image.jpg"):
    img_data = requests.get(img_url).content
    with open(filename, 'wb') as handler:
        handler.write(img_data)
    return filename


async def download_and_upload_file(url: str, client: httpx.AsyncClient, event, status_message, file_extension: str, index: int, total_files: int):
    """دانلود و آپلود همزمان فایل"""
    try:
        temp_filename = f"temp_{hash(url)}_{datetime.now().timestamp()}{file_extension}"
        response = await client.get(url, follow_redirects=True)
        
        if response.status_code != 200:
            await status_message.edit(f"❌ خطا در دانلود فایل {index} - وضعیت: {response.status_code}")
            return

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        last_update_time = 0
        
        # دانلود فایل
        with open(temp_filename, 'wb') as f:
            async for chunk in response.aiter_bytes(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                
                current_time = asyncio.get_event_loop().time()
                if current_time - last_update_time > 0.5 and total_size > 0:
                    last_update_time = current_time
                    percentage = (downloaded / total_size) * 100
                    progress_bar = create_progress_bar(percentage)
                    size_mb = downloaded / (1024 * 1024)
                    total_mb = total_size / (1024 * 1024)
                    await status_message.edit(
                        f"📥 درحال دانلود فایل {index} از {total_files}...\n"
                        f"{progress_bar}\n"
                        f"💾 {size_mb:.1f}MB / {total_mb:.1f}MB"
                    )

        # آپلود فایل
        try:
            last_update_time = 0
            
            async def progress_callback(current, total):
                nonlocal last_update_time
                current_time = asyncio.get_event_loop().time()
                
                if current_time - last_update_time > 0.5:
                    last_update_time = current_time
                    percentage = (current / total) * 100
                    progress_bar = create_progress_bar(percentage)
                    size_mb = current / (1024 * 1024)
                    total_mb = total / (1024 * 1024)
                    await status_message.edit(
                        f"📤 درحال آپلود فایل {index} از {total_files}...\n"
                        f"{progress_bar}\n"
                        f"💾 {size_mb:.1f}MB / {total_mb:.1f}MB"
                    )

            # ارسال فایل با ریپلای به پیام اصلی
            await event.client.send_file(
                event.chat_id,
                file=temp_filename,
                reply_to=event.message.id,
                supports_streaming=True if file_extension == '.mp4' else None,
                progress_callback=progress_callback
            )

        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

    except Exception as e:
        # چاپ پیغام خطا برای بررسی دقیق‌تر
        print(f"خطا در پردازش فایل {index}: {str(e)}")
        await status_message.edit(f"❌ خطا در پردازش فایل {index}: {str(e)}")

def create_progress_bar(percentage: float, width: int = 25) -> str:
    """ایجاد نوار پیشرفت"""
    filled = int(width * percentage / 100)
    empty = width - filled
    bar = '━' * filled + '─' * empty
    return f"[{bar}] {percentage:.1f}%"

async def process_instagram_link(event, message: str, status_message):
    """پردازش یک لینک اینستاگرام"""
    async with httpx.AsyncClient(timeout=60.0) as http_client:
        for attempt in range(2):  # دو بار تلاش
            try:
                # استفاده از آدرس API برای دریافت لینک‌های رسانه‌ای
                api_url = f"https://insta-ehsan.onrender.com/ehsan?url={message}"
                response = await http_client.get(api_url)
                
                # تبدیل پاسخ به JSON
                try:
                    data = response.json()
                    if isinstance(data, dict) and "data" in data:
                        for index, item in enumerate(data["data"], 1):
                            # بررسی داده‌ها
                            if "media" in item:
                                media_url = item["media"]
                                media_type = item["type"]
                                file_extension = '.jpg' if media_type == "photo" else '.mp4'
                                
                                # دانلود و ارسال فایل‌ها
                                await download_and_upload_file(
                                    media_url,
                                    http_client,
                                    event,
                                    status_message,
                                    file_extension,
                                    index,
                                    len(data["data"])
                                )
                            else:
                                await status_message.edit(f"❌ فایل {index} فاقد لینک رسانه است.")
                    else:
                        await status_message.edit("❌ داده‌ها به درستی دریافت نشدند.")
                        return
                except ValueError:
                    await status_message.edit("❌ خطا در تبدیل پاسخ به JSON")
                    return

                # در صورت موفقیت
                await status_message.edit("✅ عملیات با موفقیت انجام شد!")
                await asyncio.sleep(3)
                await status_message.delete()
                return  # خروج از تابع در صورت موفقیت

            except Exception as e:
                print(f"خطا در پردازش لینک (تلاش {attempt + 1}): {e}")
                if attempt == 0:  # اگر تلاش اول بود
                    await status_message.edit("❌ مشکل در پردازش. در حال تلاش مجدد...")
                    await asyncio.sleep(2)
                else:  # اگر تلاش دوم بود
                    await status_message.edit(f"❌ خطا در پردازش فایل {index}: {str(e)}")


async def process_instagram_link(event, message: str, status_message):
    """پردازش یک لینک اینستاگرام"""
    async with httpx.AsyncClient(timeout=60.0) as http_client:
        for attempt in range(2):  # دو بار تلاش
            try:
                # استفاده از آدرس API برای دریافت لینک‌های رسانه‌ای
                api_url = f"https://insta-ehsan.onrender.com/ehsan?url={message}"
                response = await http_client.get(api_url)
                
                # تبدیل پاسخ به JSON
                try:
                    data = response.json()
                    if isinstance(data, dict) and "data" in data:
                        for index, item in enumerate(data["data"], 1):
                            # بررسی داده‌ها
                            if "media" in item:
                                media_url = item["media"]
                                media_type = item["type"]
                                file_extension = '.jpg' if media_type == "photo" else '.mp4'
                                
                                # دانلود و ارسال فایل‌ها
                                await download_and_upload_file(
                                    media_url,
                                    http_client,
                                    event,
                                    status_message,
                                    file_extension,
                                    index,
                                    len(data["data"])
                                )
                            else:
                                await status_message.edit(f"❌ فایل {index} فاقد لینک رسانه است.")
                    else:
                        await status_message.edit("❌ داده‌ها به درستی دریافت نشدند.")
                        return
                except ValueError:
                    await status_message.edit("❌ خطا در تبدیل پاسخ به JSON")
                    return

                # در صورت موفقیت
                await status_message.edit("✅ عملیات با موفقیت انجام شد!")
                await asyncio.sleep(3)
                await status_message.delete()
                return  # خروج از تابع در صورت موفقیت

            except Exception as e:
                print(f"خطا در پردازش لینک (تلاش {attempt + 1}): {e}")
                if attempt == 0:  # اگر تلاش اول بود
                    await status_message.edit("❌ مشکل در پردازش. در حال تلاش مجدد...")
                    await asyncio.sleep(2)
                else:  # اگر تلاش دوم بود
                    await status_message.edit("❌ مشکل در پردازش. لطفا بعداً تلاش کنید.")

async def fetch_instagram_data(url):
    """ دریافت اطلاعات از API اینستاگرام """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"https://insta-ehsan.onrender.com/ehsan?url={url}") as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            print(f"خطا در دریافت اطلاعات اینستاگرام: {e}")
    return None

async def process_link(url):
    api_url = f"https://pp-don-63v4.onrender.com/?url={url}"  # آدرس API جدید
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
                        quality_links["240p"] = f"🔹 **240p**: [لینک 240p]({quality['url']})"
                    elif quality['type'] == "854x480" and not quality_links["480p"]:
                        quality_links["480p"] = f"🔹 **480p**: [لینک 480p]({quality['url']})"
                    elif quality['type'] == "1280x720" and not quality_links["720p"]:
                        quality_links["720p"] = f"🔹 **720p**: [لینک 720p]({quality['url']})"
                    elif quality['type'] == "1920x1080" and not quality_links["1080p"]:
                        quality_links["1080p"] = f"🔹 **1080p**: [لینک 1080p]({quality['url']})"

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
    api_url = f"https://open.wiki-api.ir/apis-1/SearchDivar?key=tmPiWoM-6FXRaLt-GwPgLVH-y6g6dHr-dUyLJi3&city={city}&q={query}"

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status != 200:
                return None, "⚠️ خطا در دریافت اطلاعات از دیوار."

            data = await response.json()

            if "status" in data and data["status"] == True:
                results = data["detail"][:20]  # نمایش ۱۰ نتیجه اول
                return detail, None
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
    global current_index

    async with aiohttp.ClientSession() as session:
        for _ in range(len(licenses)):  # تلاش تا آخرین لایسنس
            api_key = licenses[current_index]
            api_url = f"https://open.wiki-api.ir/apis-1/SoundcloudDownloader?key={api_key}&url={track_url}"

            try:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        track_data = data.get("detail", {}).get("data", {})

                        name = track_data.get("name", "نامشخص")
                        artist = track_data.get("artist", "نامشخص")
                        thumb_url = track_data.get("thumb")
                        duration = track_data.get("duration", "نامشخص")
                        date = track_data.get("date", "تاریخ نامشخص")
                        audio_url = track_data.get("dlink")

                        if audio_url:  # اگر لینک دانلود موجود بود، مقدار را برگردان
                            filename = f"{name}.mp3"
                            async with session.get(audio_url) as audio_response:
                                if audio_response.status == 200:
                                    with open(filename, "wb") as file:
                                        file.write(await audio_response.read())
                                    return filename, name, artist, thumb_url, duration, date
                                
                            return None, None, None, None, None, None

                    # اگر API محدود شد یا خطای 403 گرفت، لایسنس را عوض می‌کنیم
                    if response.status == 403:
                        print(f"❌ لایسنس {api_key} محدود شد. جایگزینی با بعدی...")
                        current_index = (current_index + 1) % len(licenses)

            except aiohttp.ClientError:
                print("⚠ خطا در ارتباط با API")
                return None, None, None, None, None, None

    return None, None, None, None, None, None

# جستجو در SoundCloud
async def search_soundcloud(query):
    global current_index

    async with aiohttp.ClientSession() as session:
        for _ in range(len(licenses)):  # تلاش تا آخرین لایسنس
            api_key = licenses[current_index]
            api_url = f"https://open.wiki-api.ir/apis-1/SoundcloudeSearch/?key={api_key}&q={query}"

            try:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        search_results = data.get("detail", {}).get("data", [])

                        if not search_results:
                            return None, "⚠️ هیچ نتیجه‌ای یافت نشد!"

                        # دریافت ۸ نتیجه اول
                        results = search_results[:8]  
                        formatted_results = []

                        for item in results:
                            formatted_results.append({
                                "title": item.get("title", "بدون عنوان"),
                                "link": item.get("link"),
                                "img": item["img"] if item.get("img") != "Not found" else None,
                                "description": item["description"] if item.get("description") != "Not found" else None,
                                "date": item.get("time", {}).get("date", "تاریخ نامشخص"),
                                "time": item.get("time", {}).get("time", "زمان نامشخص")
                            })

                        return formatted_results if formatted_results else None, "⚠️ هیچ نتیجه‌ای یافت نشد!"

                    # اگر API محدود شد یا خطای 403 گرفت، لایسنس را عوض می‌کنیم
                    if response.status == 403:
                        print(f"❌ لایسنس {api_key} محدود شد. جایگزینی با بعدی...")
                        current_index = (current_index + 1) % len(licenses)

            except aiohttp.ClientError:
                print("⚠ خطا در ارتباط با API")
                return None, "⚠️ مشکل در اتصال به سرور"

    return None, "⚠️ تمام لایسنس‌ها منقضی شده‌اند!"

@client.on(events.NewMessage(pattern='/on'))
async def on_handler(event):
    global robot_status
    robot_status = True
    await event.message.edit("🤖 ربات روشن شد!")

@client.on(events.NewMessage(pattern='/off'))
async def off_handler(event):
    global robot_status
    robot_status = False
    await event.message.edit("🤖 ربات خاموش شد!")

# گوش دادن به پیام‌ها
@client.on(events.NewMessage)
async def handle_message(event):
    if not robot_status:
        # اگر ربات خاموش باشد، هیچ پاسخی ارسال نمی‌شود
        return
        
    chat_id = event.chat_id
    user_id = event.sender_id
    message = event.raw_text.strip()
    message_id = event.message.id
    text = event.message.text

    if not text:
        return

    # **تشخیص لینک اینستاگرام داخل هندلر**
    insta_pattern = r'https?://(www\.)?instagram\.com/\S+'
    insta_match = re.search(insta_pattern, text)

    if insta_match:
        insta_link = insta_match.group(0)  # لینک اینستاگرام رو از متن استخراج کن

        # نمایش اکشن "در حال پردازش..."
        async with client.action(event.chat_id, "typing"):
            data = await fetch_instagram_data(insta_link)

        if data and "data" in data:
            media_files = []  # لیستی برای ذخیره لینک‌های دانلود

            for item in data["data"]:
                media_url = item.get("media")
                media_type = item.get("type")  # نوع محتوا: photo یا video
                
                if media_url and media_type:
                    # برای ویدیو
                    if media_type == "video":
                        download_link = f'<a href="{media_url}">دانلود مستقیم</a>'
                        media_files.append(f"{download_link}")
                    # برای عکس
                    elif media_type == "photo":
                        download_link = f'<a href="{media_url}">دانلود</a>'
                        media_files.append(f"برای دانلود عکس روی لینک زیر کلیک کنید:\n{download_link}")
                    else:
                        continue  # اگر نوع ناشناخته بود، رد کن

            # ارسال لینک‌های دانلود به صورت جداگانه
            if media_files:
                for file_link in media_files:
                    await event.reply(file_link, parse_mode="html")

        return

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
                img = result.get("img") if result.get("img") else None
                description = result.get("description", "بدون توضیحات")
                date = result.get("date", "تاریخ نامشخص")
                time = result.get("time", "زمان نامشخص")

                caption = (
                f"🎵 **{title}**\n"
                f"📆 **تاریخ:** {date}\n"
                f"⏰ **زمان:** {time}\n"
                f"📝 **توضیحات:** {description}\n"
                f"🔗 [لینک ساندکلاد]({link})"
                )

                # محدود کردن متن کپشن به 1000 کاراکتر برای جلوگیری از خطای طولانی بودن کپشن
                caption = caption[:950] + "..." if len(caption) > 1000 else caption

                if img:
                    await client.send_file(chat_id, img, caption=caption)
                else:
                    await event.reply(caption)
        return
            

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
    # کدهایی که از async with استفاده می‌کنند
    if "soundcloud.com" in message:
        try:
            # اطلاع‌رسانی به کاربر
            await event.reply("🎵 در حال دانلود موزیک... لطفاً صبر کنید.")

            # دریافت اطلاعات موزیک
            file_path, name, artist, thumb_url, duration, date = await download_soundcloud_audio(message)

            # بررسی اینکه آیا فایل به درستی دانلود نشده است
            if not file_path:
                await event.reply("🚫 دانلود موزیک با مشکل مواجه شد.")
                return

            # ساختن کپشن برای موزیک
            caption = f"🎶 آهنگ: {name}\n"
            caption += f"🎤 هنرمند: {artist}\n"
            caption += f"⏳ مدت زمان: {duration}\n"
            caption += f"📅 تاریخ: {date}\n"
            

            # ارسال فایل موزیک همراه با کپشن
            async with client.action(chat_id, "document"):
                await client.send_file(chat_id, file_path, caption=caption, reply_to=message_id)

            # حذف فایل پس از ارسال
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            await event.reply(f"❗️ خطا در ارسال فایل: {str(e)}")
                

@client.on(events.NewMessage(pattern=r'.*instagram\.com.*'))
async def handle_instagram(event):
    """پردازش لینک‌های اینستاگرام"""
    message = event.message.text
    status_message = await event.reply("🔄 در حال پردازش لینک... لطفا صبر کنید.")
    await process_instagram_link(event, message, status_message)

@client.on(events.NewMessage(pattern='^فال'))
async def handler(event):
    # دریافت فال
    horoscope = get_horoscope()
    
    if horoscope:
        faal_text = horoscope["faal"]
        taabir_text = horoscope["taabir"]
        img_url = horoscope["img"]
        audio_url = horoscope["audio"]

        # دانلود تصویر
        img_filename = download_image(img_url)

        # ارسال تصویر و متن به همراه کپشن
        await event.reply(
            f"<b>فال امروز شما:</b>\n\n{faal_text}\n\n"
            f"<i>تعبیر: {taabir_text}</i>\n\n",
            parse_mode='html',  # استفاده از HTML برای فرمت‌بندی متن
            file=img_filename
        )

        # ارسال فایل صوتی
        await event.reply("🎧 <i>این فایل صوتی برای شماست:</i>", parse_mode='html', file=audio_url)

        # حذف فایل تصویر بعد از ارسال
        os.remove(img_filename)
    else:
        await event.reply("❌ متاسفانه مشکلی پیش آمده است. لطفا دوباره تلاش کنید.")


@client.on(events.NewMessage(pattern=r'(?i)^استخاره$'))
async def send_estekhare(event):
    img_url = get_estekhare()
    if img_url:
        image_file = download_image(img_url)
        if image_file and os.path.exists(image_file):
            try:
                with open(image_file, "rb") as img:
                    await event.reply(file=img)  # ارسال با `open()`
                os.remove(image_file)  # حذف فایل پس از ارسال موفق
            except Exception as e:
                print(f"Error sending image: {e}")
                await event.reply("خطایی در ارسال تصویر استخاره رخ داد.")
        else:
            await event.reply("خطا در دریافت تصویر استخاره. لطفاً بعداً امتحان کنید.")
    else:
        await event.reply("خطا در دریافت اطلاعات استخاره. لطفاً بعداً امتحان کنید.")

async def main():
    await client.start()
    print("🤖 ربات فعال شد!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
