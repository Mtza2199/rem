import os
import sys
import subprocess

def install_if_missing(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])


install_if_missing("pip")

packages = [
    "rembg",
    "python-telegram-bot",
    "Pillow"
]

for package in packages:
    install_if_missing(package)

os.system("clear")

import os
from rembg import remove
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.error import TimedOut

# ضع التوكن الخاص بك هنا
TOKEN = '8074949920:AAGR7IsOgV03PZ5TF1eVrJ1EGLKRlzhdaMg'

# إنشاء المجلدات الضرورية إذا لم تكن موجودة
os.makedirs('./toktok', exist_ok=True)
os.makedirs('./processed', exist_ok=True)

# دالة المساعدة
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='اهلا وسهلا بكم في بوت ازالة الخلفية للصور. ابدأ باستخدام الأمر /start'
    )

# دالة بدء التشغيل
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='أرسل الصورة لإزالة الخلفيه.'
    )

# دالة معالجة الصور
async def process_image(photo_name: str):
    name, _ = os.path.splitext(photo_name)
    output_photo_path = f'./processed/{name}.png'
    input_path = f'./toktok/{photo_name}'
    
    # إزالة الخلفية باستخدام مكتبة rembg
    input_image = Image.open(input_path)
    output_image = remove(input_image)
    output_image.save(output_photo_path)
    
    # حذف الصورة الأصلية بعد المعالجة
    os.remove(input_path)
    return output_photo_path

# دالة معالجة الرسائل
async def handler_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # التحقق من نوع الملف (صورة أو مستند)
        if filters.PHOTO.check_update(update):
            file_id = update.message.photo[-1].file_id
            unique_fil_id = update.message.photo[-1].file_unique_id
            photo_name = f"{unique_fil_id}.jpg"
        elif filters.Document.IMAGE.check_update(update):
            file_id = update.message.document.file_id
            _, f_ext = os.path.splitext(update.message.document.file_name)
            unique_fil_id = update.message.document.file_unique_id
            photo_name = f'{unique_fil_id}.{f_ext}'
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="الملف المرسل ليس صورة.")
            return

        # تحميل الملف
        photo_file = await context.bot.get_file(file_id)
        await photo_file.download_to_drive(custom_path=f'./toktok/{photo_name}')
        await context.bot.send_message(chat_id=update.effective_chat.id, text='الرجاء الانتظار...')

        # معالجة الصورة
        processed_image = await process_image(photo_name)
        await context.bot.send_document(chat_id=update.effective_chat.id, document=processed_image)

        # إرسال رسالة شكر بعد إرسال الصورة
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="شكرًا على استخدامك البوت! لا تنسَ الانضمام إلى قناتنا الخاصة: @o_cc11"
        )

        # حذف الصورة المعالجة بعد الإرسال
        os.remove(processed_image)

    except TimedOut:
        # تجاوز خطأ TimedOut دون إشعار المستخدم
        pass
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"حدث خطأ: {e}")

# نقطة البداية
if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    # تسجيل الأوامر
    help_handler = CommandHandler('help', help)
    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.PHOTO | filters.Document.IMAGE, handler_message)

    application.add_handler(help_handler)
    application.add_handler(start_handler)
    application.add_handler(message_handler)

    # تشغيل البوت
    application.run_polling()
