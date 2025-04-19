import os
import random
from pyrogram import Client, filters

# اطلاعات مربوط به API و Session
API_ID = 18377832  # مقدار API ID خود را از my.telegram.org دریافت کنید
API_HASH = "ed8556c450c6d0fd68912423325dd09c"  # مقدار API Hash خود را از my.telegram.org دریافت کنید
SESSION_NAME = "my_session"  # می‌توانید نام دلخواهی برای سشن انتخاب کنید

# ایجاد کلاینت Pyrogram
app = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH)

@app.on_message(filters.photo & filters.private)
async def onphoto(client, message):
    try:
        if message.photo.ttl_seconds:  # بررسی اینکه عکس زمان‌دار است
            rand = random.randint(1000, 9999999)
            local_path = f"downloads/photo-{rand}.png"
            
            # ایجاد پوشه دانلود در صورت عدم وجود
            if not os.path.exists("downloads"):
                os.makedirs("downloads")

            # دانلود عکس
            await message.download(file_name=local_path)

            # ارسال عکس به پیام‌های ذخیره‌شده کاربر
            await app.send_photo(
                "me",
                photo=local_path,
                caption=f"🥸@Abj0o {message.date} | Time: {message.photo.ttl_seconds}s"
            )

            # حذف فایل از سرور پس از ارسال موفق
            if os.path.exists(local_path):
                os.remove(local_path)
    
    except Exception as e:
        print(f"Error: {e}")

@app.on_message(filters.video & filters.private)
async def onvideo(client, message):
    try:
        if message.video.ttl_seconds: 
            rand = random.randint(1000, 9999999)
            local_path = f"downloads/video-{rand}.mp4"
            
            # ایجاد I'mپوشه دانلود در صورت عدم وجود
            if not os.path.exists("downloads"):
                os.makedirs("downloads")
            
            # دانلود و ذخیره ویدیو
            await message.download(file_name=local_path)
            
            # ارسال ویدیو به پیام‌های ذخیره‌شده کاربر
            await app.send_video(
                "me", 
                video=local_path, 
                caption=f"🥸 @Abj0o {message.date} | Time: {message.video.ttl_seconds}s"
            )
            
            # حذف فایل از سرور پس از ارسال موفق
            if os.path.exists(local_path):
                os.remove(local_path)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    app.run()
