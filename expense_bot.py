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
    
    def _get_or_create_sheet(self, sheet_name: str = "Gastos"):
        """Get existing sheet or create a new one with headers."""
        try:
            # Try to open existing spreadsheet first
            try:
                spreadsheet = self.gc.open(sheet_name)
                self.sheet = spreadsheet.sheet1
                logger.info(f"Opened existing spreadsheet: {sheet_name}")
                return True
            except gspread.SpreadsheetNotFound:
                logger.info(f"Spreadsheet '{sheet_name}' not found, trying alternative methods...")
                
                # Try to find sheet by searching all available sheets
                try:
                    all_sheets = self.gc.openall()
                    for sheet in all_sheets:
                        if "gasto" in sheet.title.lower():
                            spreadsheet = sheet
                            self.sheet = spreadsheet.sheet1
                            logger.info(f"Found sheet with 'gasto' in name: {sheet.title}")
                            return True
                except Exception as e:
                    logger.warning(f"Could not search through sheets: {e}")
                
                logger.info(f"Will try to create new spreadsheet: {sheet_name}")
            
            # Try to create new spreadsheet if it doesn't exist
            try:
                spreadsheet = self.gc.create(sheet_name)
                self.sheet = spreadsheet.sheet1
                
                # Add headers
                headers = ["FECHA DEL GASTO", "PRODUCTO", "LUGAR", "CATEGORIA", "SUB CATEGORIA", "IMPORTE", "CANTIDAD"]
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
        
        # Validate message format (exactly 6 lines)
        if len(lines) != 6:
            return None
        
        try:
            # Extract data from lines
            product = lines[0]
            place = lines[1]  # LUGAR (place/location)
            category = lines[2]
            subcategory = lines[3]
            amount = float(lines[4])  # Validate amount is numeric
            quantity = int(lines[5])  # Validate quantity is integer
            
            # Add current date
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return {
                "date": current_date,
                "product": product,
                "place": place,
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
            
            # Prepare row data matching your sheet structure
            row_data = [
                expense_data["date"],
                expense_data["product"],
                expense_data["place"],
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
¡Bienvenido al Bot de Gastos! 💰

Envíame tus gastos en este formato (cada elemento en una línea nueva):

Producto
Lugar
Categoría
Subcategoría
Importe
Cantidad

Ejemplo:
Harina
Panadería
Comida
Productos básicos
1200
2

Lo registraré automáticamente en tu hoja de Google con la fecha y hora actual.
    """
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    help_message = """
📋 Cómo usar este bot:

1. Envíame un mensaje con los detalles de tu gasto en exactamente 6 líneas:
   Línea 1: Nombre del producto
   Línea 2: Lugar de compra
   Línea 3: Categoría
   Línea 4: Subcategoría  
   Línea 5: Importe (número)
   Línea 6: Cantidad (número)

2. Automáticamente agregaré la fecha actual y lo guardaré en tu hoja de Google.

3. Asegúrate de que tu mensaje tenga exactamente 6 líneas y que el importe y cantidad sean números válidos.

Ejemplo:
Pan
Panadería
Comida
Productos básicos
2500
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
❌ ¡Formato de mensaje inválido!

Por favor envía exactamente 6 líneas:
1. Nombre del producto
2. Lugar de compra
3. Categoría
4. Subcategoría
5. Importe (número)
6. Cantidad (número)

Ejemplo:
Harina
Panadería
Comida
Productos básicos
1200
2
            """
            await update.message.reply_text(error_message)
            return
        
        # Ensure sheet is ready
        if not expense_bot.sheet:
            if not expense_bot._get_or_create_sheet():
                if getattr(expense_bot, 'quota_exceeded', False):
                    await update.message.reply_text("❌ Cuota de almacenamiento de Google Drive excedida. Por favor libera espacio en tu Google Drive o crea una hoja llamada 'Gastos' manualmente e inténtalo de nuevo.")
                else:
                    await update.message.reply_text("❌ Error al conectar con Google Sheets. Por favor inténtalo más tarde.")
                return
        
        # Log expense to sheet
        success = expense_bot._log_expense_to_sheet(expense_data)
        
        if success:
            success_message = f"""
✅ ¡Gasto registrado exitosamente!

📅 Fecha: {expense_data['date']}
🛍️ Producto: {expense_data['product']}
📍 Lugar: {expense_data['place']}
📂 Categoría: {expense_data['category']}
📁 Subcategoría: {expense_data['subcategory']}
💰 Importe: {expense_data['amount']}
📦 Cantidad: {expense_data['quantity']}
            """
            await update.message.reply_text(success_message)
        else:
            await update.message.reply_text("❌ Error al registrar el gasto. Por favor inténtalo más tarde.")
            
    except Exception as e:
        logger.error(f"Error handling expense message: {e}")
        await update.message.reply_text("❌ Ocurrió un error al procesar tu gasto. Por favor inténtalo de nuevo.")

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
            logger.warning("Google Drive quota exceeded. Bot will start but users need to free up space or create 'Gastos' sheet manually.")
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
        logger.info("Iniciando Bot de Gastos...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    main()
