import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
from datetime import datetime

# 1. تحميل الإعدادات
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
AFFILIATE_LINK = os.getenv('AFFILIATE_LINK')

# 2. إعداد السجلات (Logging)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# مخزن مؤقت للمنتجات
saved_products = {}

# 3. الدوال البرمجية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "🤖 **مرحباً بك في بوت علي إكسبريس**\n\nاستخدم /help لعرض الأوامر المتاحة."
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📋 **أوامر البوت المتاحة:**

/add_product - إضافة منتج جديد
/list_products - عرض المنتجات المحفوظة
/publish - نشر المنتجات في القناة
/stats - إحصائيات سريعة
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['adding_product'] = True
    await update.message.reply_text("📝 أرسل الآن **اسم المنتج**:")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    if context.user_data.get('adding_product'):
        # نظام الخطوات لإضافة المنتج
        if 'product_name' not in context.user_data:
            context.user_data['product_name'] = user_message
            await update.message.reply_text("🔗 أرسل **رابط المنتج** من علي إكسبريس:")
        elif 'product_link' not in context.user_data:
            context.user_data['product_link'] = user_message
            await update.message.reply_text("💰 أرسل **سعر المنتج** (مثال: 15$):")
        elif 'price' not in context.user_data:
            context.user_data['price'] = user_message
            await update.message.reply_text("📝 أرسل **وصفاً مختصراً** للمنتج:")
        elif 'description' not in context.user_data:
            context.user_data['description'] = user_message
            
            # حفظ المنتج في القائمة
            product_id = len(saved_products) + 1
            saved_products[product_id] = {
                'name': context.user_data['product_name'],
                'link': context.user_data['product_link'],
                'price': context.user_data['price'],
                'description': context.user_data['description']
            }
            
            await update.message.reply_text(f"✅ تم حفظ المنتج بنجاح! ID: {product_id}\nاستخدم /publish للنشر.")
            context.user_data.clear()

async def publish_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not saved_products:
        await update.message.reply_text("❌ لا توجد منتجات بانتظار النشر!")
        return
    
    try:
        for pid, p in saved_products.items():
            # دمج رابط الأفلييت الخاص بك تلقائياً
            final_link = f"{p['link']}?{AFFILIATE_LINK}" if AFFILIATE_LINK else p['link']
            
            message = f"🛍️ **{p['name']}**\n\n💰 السعر: {p['price']}\n\n📝 {p['description']}\n\n🔗 [اشتري الآن من هنا]({final_link})"
            
            await context.bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode='Markdown')
        
        await update.message.reply_text(f"✅ تم نشر {len(saved_products)} منتجات في القناة!")
        saved_products.clear()
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ أثناء النشر: {str(e)}")

# 4. تشغيل البوت
def main():
    # بناء التطبيق
    app = Application.builder().token(BOT_TOKEN).build()
    
    # إضافة الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("add_product", add_product))
    app.add_handler(CommandHandler("publish", publish_products))
    
    # معالجة الرسائل النصية
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # تشغيل البوت بوضع polling المتوافق مع Render
    print("Bot is starting...")
    app.run_polling()

if __name__ == '__main__':
    main()


