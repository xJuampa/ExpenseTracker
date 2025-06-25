from flask import Flask, request, jsonify
from threading import Thread
import json

app = Flask(__name__)

# Global variable to store bot instance
bot_instance = None

@app.route('/')
def home():
    return "Bot is alive!"

@app.route('/status')
def status():
    """Check bot status"""
    return jsonify({
        "status": "running",
        "bot_connected": bot_instance is not None,
        "message": "Bot de gastos funcionando correctamente"
    })

@app.route('/add_expense', methods=['POST'])
def add_expense():
    """Add expense via API"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se proporcionaron datos"}), 400
        
        # Validate required fields
        required_fields = ['producto', 'lugar', 'categoria', 'subcategoria', 'importe', 'cantidad']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({"error": f"Faltan campos requeridos: {', '.join(missing_fields)}"}), 400
        
        if bot_instance is None:
            return jsonify({"error": "Bot no está inicializado"}), 500
        
        # Create expense data in the same format as telegram messages
        from datetime import datetime
        expense_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'product': str(data['producto']),
            'place': str(data['lugar']),
            'category': str(data['categoria']),
            'subcategory': str(data['subcategoria']),
            'amount': str(data['importe']),
            'quantity': str(data['cantidad'])
        }
        
        # Use bot's method to log expense
        success = bot_instance._log_expense_to_sheet(expense_data)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Gasto registrado exitosamente",
                "data": {
                    "producto": data['producto'],
                    "lugar": data['lugar'],
                    "categoria": data['categoria'],
                    "subcategoria": data['subcategoria'],
                    "importe": data['importe'],
                    "cantidad": data['cantidad'],
                    "fecha": expense_data['date']
                }
            })
        else:
            return jsonify({"error": "Error al registrar el gasto en Google Sheets"}), 500
            
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@app.route('/help')
def help_endpoint():
    """API help endpoint"""
    return jsonify({
        "endpoints": {
            "/": "Check if bot is alive",
            "/status": "Get bot status",
            "/add_expense": "Add expense (POST with JSON data)",
            "/help": "This help message"
        },
        "add_expense_format": {
            "method": "POST",
            "content_type": "application/json",
            "body": {
                "producto": "Nombre del producto",
                "lugar": "Lugar de compra",
                "categoria": "Categoría",
                "subcategoria": "Subcategoría", 
                "importe": "Precio",
                "cantidad": "Cantidad"
            }
        },
        "example": {
            "producto": "Pan",
            "lugar": "Panadería",
            "categoria": "Comida",
            "subcategoria": "Productos básicos",
            "importe": "2500",
            "cantidad": "1"
        }
    })

def set_bot_instance(bot):
    """Set the bot instance for API access"""
    global bot_instance
    bot_instance = bot

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()