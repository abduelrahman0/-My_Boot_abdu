import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import yt_dlp

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "9109580855:AAFE4nAV3E3YXQC5JCMQcLHzkCHIM6sRTMk"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text and (text.startswith("http://") or text.startswith("https://")):
        sent_message = await update.message.reply_text("⏳ جاري تحليل الرابط وتحميل الفيديو، يرجى الانتظار...")
        
        output_template = '%(id)s.%(ext)s'
        ydl_opts = {
            'format': 'best',
            'outtmpl': output_template,
            'max_filesize': 50 * 1024 * 1024,
        }
        
        video_filename = None
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(text, download=True)
                video_filename = ydl.prepare_filename(info)
            
            await update.message.reply_video(video=open(video_filename, 'rb'))
            await sent_message.delete()
            
        except yt_dlp.utils.DownloadError:
            await sent_message.edit_text("❌ عذراً، لم أتمكن من تحميل الفيديو من هذا الرابط. تأكد أن الرابط صحيح أو أن الفيديو متاح للعامة.")
        except Exception as e:
            await sent_message.edit_text("❌ حدث خطأ أثناء المعالجة: حجم الملف قد يكون كبيراً جداً أو صيغته غير مدعومة.")
        finally:
            if video_filename and os.path.exists(video_filename):
                os.remove(video_filename)
    else:
        await update.message.reply_text("الرجاء إرسال رابط صالح لفيديو من أي موقع.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("🤖 البوت يعمل الآن ويستمع للروابط...")
    app.run_polling()
