# Extensions Module for AliExpress Bot
# Add custom features and commands here

# Example: Custom command template
# async def my_custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("Custom command response")

# Add your extensions below:
# Add your custom commands here
async def my_custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Your custom response")
