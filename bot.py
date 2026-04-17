import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telethon import TelegramClient, events
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

# Load environment variables
load_dotenv()

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME')
AFFILIATE_LINK = os.getenv('AFFILIATE_LINK')
PORT = int(os.getenv('PORT', 8080))

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Telethon client for monitoring
telethon_client = TelegramClient('session', API_ID, API_HASH)

# Dictionary to store drafts data
saved_products = {}

def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_text = """
🤖 **Welcome to AliExpress Bot**

This bot helps you manage and publish AliExpress products with affiliate links.

**Available Commands:**
/help - Show all commands
/add_product - Add a new product
/list_products - View all products
/publish - Publish products to channel
/discounts - Manage discount codes
/stats - View bot statistics
/settings - Configure bot settings
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
📋 **Bot Commands Help**

**Product Management:**
/add_product - Add new AliExpress product
/list_products - Display all saved products
/delete_product <id> - Remove a product
/edit_product <id> - Modify product details

**Publishing:**
/publish - Publish ready products to channel
/schedule_publish <time> - Schedule automatic publishing

**Discounts & Coupons:**
/add_discount <code> <percentage> - Add discount code
/list_discounts - Show all active discounts
/remove_discount <code> - Delete discount

**Statistics:**
/stats - View channel statistics
/product_stats - Product performance metrics

**Settings:**
/set_channel <channel> - Set target channel
/set_affiliate <link> - Update affiliate link
/language - Change language
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /add_product command"""
    context.user_data['adding_product'] = True
    reply_text = """
📝 **Add New Product**

Please provide the following information:

1️⃣ **Product Name:**
2️⃣ **Product Link:** (AliExpress link)
3️⃣ **Price:** (with currency)
4️⃣ **Description:** (in English)
5️⃣ **Images:** (optional)

Start by typing the product name:
    """
    await update.message.reply_text(reply_text, parse_mode='Markdown')

def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages"""
    user_message = update.message.text
    
    if context.user_data.get('adding_product'):
        # Handle product adding flow
        if 'product_name' not in context.user_data:
            context.user_data['product_name'] = user_message
            await update.message.reply_text("Now enter the AliExpress product link:")
        elif 'product_link' not in context.user_data:
            context.user_data['product_link'] = user_message
            await update.message.reply_text("Enter the price:")
        elif 'price' not in context.user_data:
            context.user_data['price'] = user_message
            await update.message.reply_text("Enter product description (in English):")
        elif 'description' not in context.user_data:
            context.user_data['description'] = user_message
            
            # Save product
            product_id = len(saved_products) + 1
            saved_products[product_id] = {
                'name': context.user_data['product_name'],
                'link': context.user_data['product_link'],
                'price': context.user_data['price'],
                'description': context.user_data['description'],
                'created_at': datetime.now().isoformat()
            }
            
            await update.message.reply_text(
                f"✅ Product saved successfully!\n\nProduct ID: {product_id}\n\nUse /publish to publish this product."
            )
            context.user_data['adding_product'] = False

def publish_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Publish products to channel"""
    if not saved_products:
        await update.message.reply_text("❌ No products to publish!")
        return
    
    try:
        for product_id, product in saved_products.items():
            # Create marketing message with affiliate link
            message = f"""
🛍️ **{product['name']}**

💰 **Price:** {product['price']}

📝 **Description:**
{product['description']}

🔗 **Get it now:**
{product['link']}?{AFFILIATE_LINK}

⏰ Limited time offer! Don't miss out!

#AliExpress #Shopping #Deal #Products
            """
            # Send to channel
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=message,
                parse_mode='Markdown'
            )
        
        await update.message.reply_text(f"✅ Published {len(saved_products)} products successfully!")
    except Exception as e:
        logger.error(f"Error publishing products: {e}")
        await update.message.reply_text(f"❌ Error publishing: {str(e)}")

async def list_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all saved products"""
    if not saved_products:
        await update.message.reply_text("📭 No products saved yet!")
        return
    
    message = "📦 **Saved Products:**\n\n"
    for pid, product in saved_products.items():
        message += f"ID: {pid}\n"
        message += f"Name: {product['name']}\n"
        message += f"Price: {product['price']}\n"
        message += f"---\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def add_discount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /add_discount command"""
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /add_discount <code> <percentage>")
        return
    
    code = context.args[0]
    percentage = context.args[1]
    
    if 'discounts' not in context.user_data:
        context.user_data['discounts'] = {}
    
    context.user_data['discounts'][code] = percentage
    await update.message.reply_text(f"✅ Discount code '{code}' ({percentage}% off) added!")
    
async def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add_product", add_product))
    application.add_handler(CommandHandler("list_products", list_products))
    application.add_handler(CommandHandler("publish", publish_products))
    application.add_handler(CommandHandler("add_discount", add_discount))
    
    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    logger.info("Bot started successfully!")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
import os
import json

load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
AFFILIATE_LINK = os.getenv('AFFILIATE_LINK')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎉 Welcome to AliExpress Bot!\nUse /help for commands")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📋 **Available Commands:**
/start - Start bot
/add_product - Add new product
/list_products - View products
/publish - Publish to channel
/add_discount - Create discount
/stats - View statistics
    """
    await update.message.reply_text(help_text)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.run_polling()

if __name__ == '__main__':
    main()
