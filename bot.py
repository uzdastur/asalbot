import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler, CallbackQueryHandler
from io import BytesIO
from reportlab.pdfgen import canvas

# 📌 Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 🔐 Token — TO‘G‘RIDAN-TO‘G‘RI QO‘YILDI
BOT_TOKEN = "7446776697:AAFv1kl4lnotC0exrSJJZnY4ujNdJFC1eBk"

# 🗃️ Vaqtincha buyurtmalar
orders = []

# 📋 Menyu
def main_menu():
    keyboard = [
        [InlineKeyboardButton("📝 Yangi buyurtma yuborish", callback_data='new_order')],
        [InlineKeyboardButton("📄 PDF chiqazish", callback_data='get_pdf')],
        [InlineKeyboardButton("📁 README faylni yuborish", callback_data='send_file')],
        [InlineKeyboardButton("ℹ️ Yordam", callback_data='help')]
    ]
    return InlineKeyboardMarkup(keyboard)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "👋 Xush kelibsiz! Bu bot orqali buyurtma yuborishingiz mumkin.\nQuyidagi menyudan foydalaning:",
            reply_markup=main_menu()
        )
    except Exception as e:
        logger.error(f"/start komandasi xatosi: {e}")

# Matnli buyurtma
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.message.from_user
        text = update.message.text.strip()
        if text:
            orders.append({
                "user_name": user.full_name,
                "user_id": user.id,
                "text": text
            })
            await update.message.reply_text("✅ Buyurtmangiz qabul qilindi!", reply_markup=main_menu())
        else:
            await update.message.reply_text("❗ Iltimos, bo‘sh xabar yubormang.")
    except Exception as e:
        logger.error(f"Xabarni qabul qilishda xatolik: {e}")
        await update.message.reply_text("❌ Xatolik yuz berdi.")

# Tugmalar
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        if query.data == 'get_pdf':
            if not orders:
                await query.message.reply_text("⛔ Buyurtmalar yo‘q.")
                return

            buffer = BytesIO()
            p = canvas.Canvas(buffer)
            y = 800

            for order in orders:
                p.drawString(50, y, f"{order['user_name']} ({order['user_id']}): {order['text']}")
                y -= 20
                if y < 100:
                    p.showPage()
                    y = 800

            p.save()
            buffer.seek(0)
            await query.message.reply_document(document=InputFile(buffer, filename="orders.pdf"))

        elif query.data == 'send_file':
            file_path = "README.txt"
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("Bu bot orqali buyurtmalar qabul qilinadi.")
                await query.message.reply_document(document=InputFile(file_path))
            except Exception as e:
                logger.error(f"Fayl yozishda xatolik: {e}")
                await query.message.reply_text("❌ README fayl yuborishda xatolik.")

        elif query.data == 'new_order':
            await query.message.reply_text("✍️ Yangi buyurtmangizni yozib yuboring.")

        elif query.data == 'help':
            await query.message.reply_text("ℹ️ Bu bot buyurtmalarni qabul qiladi. /start bilan boshlang.")

    except Exception as e:
        logger.error(f"Tugmani qayta ishlashda xatolik: {e}")
        await query.message.reply_text("❌ Amalni bajarishda xatolik yuz berdi.")

# Ishga tushirish
def main():
    try:
        app = Application.builder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        app.add_handler(CallbackQueryHandler(button_handler))

        logger.info("🤖 Bot ishga tushdi.")
        app.run_polling()
    except Exception as e:
        logger.critical(f"Botni ishga tushirishda xatolik: {e}")

if __name__ == "__main__":
    main()
