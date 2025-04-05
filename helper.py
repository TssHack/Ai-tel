from pyrogram import Client, filters
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

# اطلاعات ربات
API_ID = 18377832       # مقدار api_id از my.telegram.org
API_HASH = "ed8556c450c6d0fd68912423325dd09c"  # مقدار api_hash از my.telegram.org
BOT_TOKEN = "7000850548:AAHm8y3bG6LGm0l1agzXfhpyR4gDGceB5NI"

# ساخت کلاینت ربات
app = Client("helper_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# لیست دکمه‌ها و توضیحات
descriptions = {
    "help_porn": "🔞 ارسال لینک سایت‌های بزرگسال مانند Pornhub/Xvideos → انتخاب کیفیت → دریافت ویدیو در تلگرام.",
    "help_instagram": "📸 ارسال لینک پست اینستاگرام → دریافت ویدیو یا تصاویر همراه با لینک دانلود مستقیم.",
    "help_soundcloud": "🎧 ارسال `ehsan کلمه‌کلیدی` → جستجو در SoundCloud و دریافت لینک و کاور موزیک.",
    "help_ai": "🧠 ارسال پیام با `ai` در ابتدا → پاسخ‌دهی توسط هوش مصنوعی.",
    "help_faal": "🔮 ارسال `فال` → دریافت فال روز همراه با تعبیر، عکس و فایل صوتی.",
    "help_dl": "💾 ارسال `dl` روی مدیای ریپلای شده → ذخیره در Saved Messages.",
    "help_chart": "📈 ارسال `search? BTCUSDT 1h` → دریافت چارت لحظه‌ای از بازار کریپتو."
}

# هندلر اینلاین کوئری
@app.on_inline_query()
async def answer_inline(client, inline_query):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔞 بزرگسال", callback_data="help_porn")],
        [InlineKeyboardButton("📸 اینستاگرام", callback_data="help_instagram")],
        [InlineKeyboardButton("🎧 ساندکلاد", callback_data="help_soundcloud")],
        [InlineKeyboardButton("🧠 هوش مصنوعی", callback_data="help_ai")],
        [InlineKeyboardButton("🔮 فال", callback_data="help_faal")],
        [InlineKeyboardButton("💾 ذخیره مدیا", callback_data="help_dl")],
        [InlineKeyboardButton("📈 چارت", callback_data="help_chart")]
    ])

    result = InlineQueryResultArticle(
        title="راهنمای ربات",
        description="دریافت توضیح تمام قابلیت‌های ربات شما",
        input_message_content=InputTextMessageContent(
            "🧠 پنل راهنمای ربات:\n\nبرای مشاهده توضیح هر بخش روی دکمه‌های زیر کلیک کنید.",
        ),
        reply_markup=keyboard
    )

    await inline_query.answer([result], cache_time=1, is_personal=True)

# هندلر دکمه‌ها
@app.on_callback_query()
async def handle_callback(client, callback_query):
    data = callback_query.data
    description = descriptions.get(data)

    if description:
        await callback_query.answer()
        await callback_query.message.edit_text(
            f"<b>راهنمای قابلیت:</b>\n\n{description}",
            parse_mode="html",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت به پنل", switch_inline_query_current_chat="help")]
            ])
        )
    else:
        await callback_query.answer("❌ این بخش پیدا نشد!", show_alert=True)

# اجرای ربات
app.run()
