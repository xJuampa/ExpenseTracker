import os
import json
import logging
from datetime import datetime
from typing import Optional

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ExpenseBot:
    def __init__(self):
        """Initialize the expense bot with Google Sheets and Telegram integration."""
        self.bot_token = os.getenv("BOT_TOKEN")
        self.google_creds_json = os.getenv("GOOGLE_CREDS")
        
        if not self.bot_token:
            raise ValueError("BOT_TOKEN environment variable is required")
        
        if not self.google_creds_json:
            raise ValueError("GOOGLE_CREDS environment variable is required")
        
        # Initialize Google Sheets client
        self.gc = None
        self.sheet = None
        self.quota_exceeded = False
        self._setup_google_sheets()
    
    def _setup_google_sheets(self):
        """Setup Google Sheets authentication and connection."""
        try:
            # Parse credentials from environment variable
            creds_dict = json.loads(self.google_creds_json)
            
            # Define the scope for Google Sheets API
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Create credentials object
            credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            
            # Authorize and create gspread client
            self.gc = gspread.authorize(credentials)
            
            logger.info("Google Sheets authentication successful")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Google credentials JSON: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to setup Google Sheets: {e}")
            raise
    
    def _get_or_create_sheet(self, sheet_name: str = "Expenses"):
        """Get existing sheet or create a new one with headers."""
        try:
            # Try to open existing spreadsheet first
            try:
                spreadsheet = self.gc.open(sheet_name)
                self.sheet = spreadsheet.sheet1
                logger.info(f"Opened existing spreadsheet: {sheet_name}")
                return True
            except gspread.SpreadsheetNotFound:
                logger.info(f"Spreadsheet '{sheet_name}' not found, will try to create it")
            
            # Try to create new spreadsheet if it doesn't exist
            try:
                spreadsheet = self.gc.create(sheet_name)
                self.sheet = spreadsheet.sheet1
                
                # Add headers
                headers = ["Date", "Product", "Category", "Subcategory", "Amount", "Quantity"]
                self.sheet.append_row(headers)
                
                logger.info(f"Created new spreadsheet with headers: {sheet_name}")
                return True
                
            except Exception as create_error:
                if "quota" in str(create_error).lower() or "403" in str(create_error):
                    logger.error(f"Google Drive storage quota exceeded. Please free up space or use an existing spreadsheet.")
                    # Set a flag to indicate quota issue
                    self.quota_exceeded = True
                    return False
                else:
                    raise create_error
            
        except Exception as e:
            logger.error(f"Failed to setup spreadsheet: {e}")
            return False
    
    def _parse_expense_message(self, message_text: str) -> Optional[dict]:
        """Parse expense message and return structured data."""
        lines = [line.strip() for line in message_text.strip().split('\n') if line.strip()]
        
        # Validate message format (exactly 5 lines)
        if len(lines) != 5:
            return None
        
        try:
            # Extract data from lines
            product = lines[0]
            category = lines[1]
            subcategory = lines[2]
            amount = float(lines[3])  # Validate amount is numeric
            quantity = int(lines[4])  # Validate quantity is integer
            
            # Add current date
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return {
                "date": current_date,
                "product": product,
                "category": category,
                "subcategory": subcategory,
                "amount": amount,
                "quantity": quantity
            }
            
        except (ValueError, IndexError) as e:
            logger.error(f"Failed to parse expense data: {e}")
            return None
    
    def _log_expense_to_sheet(self, expense_data: dict) -> bool:
        """Log expense data to Google Sheet."""
        try:
            # Ensure sheet is available
            if not self.sheet:
                if not self._get_or_create_sheet():
                    return False
            
            # Prepare row data
            row_data = [
                expense_data["date"],
                expense_data["product"],
                expense_data["category"],
                expense_data["subcategory"],
                expense_data["amount"],
                expense_data["quantity"]
            ]
            
            # Append row to sheet
            self.sheet.append_row(row_data)
            
            logger.info(f"Successfully logged expense: {expense_data['product']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log expense to sheet: {e}")
            return False

# Telegram bot handlers
expense_bot = ExpenseBot()

async def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    welcome_message = """
Welcome to the Expense Tracker Bot! 📊

Send me your expenses in this format (each item on a new line):

Product
Category  
Subcategory
Amount
Quantity

Example:
Harina
comida
panaderia
1200
2

I'll automatically log it to your Google Sheet with the current date and time.
    """
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    help_message = """
📋 How to use this bot:

1. Send me a message with your expense details in exactly 5 lines:
   Line 1: Product name
   Line 2: Category
   Line 3: Subcategory  
   Line 4: Amount (number)
   Line 5: Quantity (whole number)

2. I'll automatically add the current date and save it to your Google Sheet.

3. Make sure your message has exactly 5 lines and the amount/quantity are valid numbers.

Example:
Bread
Food
Bakery
5.50
1
    """
    await update.message.reply_text(help_message)

async def handle_expense_message(update: Update, context: CallbackContext) -> None:
    """Handle incoming expense messages."""
    try:
        message_text = update.message.text
        
        # Parse the expense message
        expense_data = expense_bot._parse_expense_message(message_text)
        
        if not expense_data:
            error_message = """
❌ Invalid message format!

Please send exactly 5 lines:
1. Product name
2. Category
3. Subcategory
4. Amount (number)
5. Quantity (whole number)

Example:
Harina
comida
panaderia
1200
2
            """
            await update.message.reply_text(error_message)
            return
        
        # Ensure sheet is ready
        if not expense_bot.sheet:
            if not expense_bot._get_or_create_sheet():
                if getattr(expense_bot, 'quota_exceeded', False):
                    await update.message.reply_text("❌ Google Drive storage quota exceeded. Please free up space in your Google Drive or create a spreadsheet named 'Expenses' manually and try again.")
                else:
                    await update.message.reply_text("❌ Failed to connect to Google Sheets. Please try again later.")
                return
        
        # Log expense to sheet
        success = expense_bot._log_expense_to_sheet(expense_data)
        
        if success:
            success_message = f"""
✅ Expense logged successfully!

📅 Date: {expense_data['date']}
🛍️ Product: {expense_data['product']}
📂 Category: {expense_data['category']}
📁 Subcategory: {expense_data['subcategory']}
💰 Amount: {expense_data['amount']}
📦 Quantity: {expense_data['quantity']}
            """
            await update.message.reply_text(success_message)
        else:
            await update.message.reply_text("❌ Failed to log expense. Please try again later.")
            
    except Exception as e:
        logger.error(f"Error handling expense message: {e}")
        await update.message.reply_text("❌ An error occurred while processing your expense. Please try again.")

async def error_handler(update: Update, context: CallbackContext) -> None:
    """Log errors caused by updates."""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Start the bot."""
    try:
        # Try to setup Google Sheets connection, but continue even if it fails
        # The bot will handle the error when users try to log expenses
        expense_bot._get_or_create_sheet()
        
        if getattr(expense_bot, 'quota_exceeded', False):
            logger.warning("Google Drive quota exceeded. Bot will start but users need to free up space or create 'Expenses' sheet manually.")
        elif not expense_bot.sheet:
            logger.warning("Could not setup Google Sheets initially. Bot will try again when users send expenses.")
        
        # Create the Application
        application = Application.builder().token(expense_bot.bot_token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_expense_message))
        
        # Add error handler
        application.add_error_handler(error_handler)
        
        # Start the bot
        logger.info("Starting Expense Tracker Bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    main()
