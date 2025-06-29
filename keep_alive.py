from flask import Flask, request, jsonify
from threading import Thread
import json
import os
from datetime import datetime

app = Flask(__name__)

# Global variable to store bot instance
bot_instance = None

@app.route('/')
def home():
    return """
    <html>
    <head>
        <title>Bot de Gastos - Status</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .status { color: #28a745; font-weight: bold; }
            .endpoint { background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 5px; }
            code { background: #e9ecef; padding: 2px 5px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Bot de Gastos</h1>
            <p class="status">✅ Bot funcionando correctamente</p>
            <p><strong>Última verificación:</strong> {}</p>
            
            <h2>📡 Endpoints disponibles:</h2>
            <div class="endpoint">
                <code>/status</code> - Estado del bot en JSON
            </div>
            <div class="endpoint">
                <code>/add_expense</code> - Agregar gasto via API (POST)
            </div>
            <div class="endpoint">
                <code>/help</code> - Ayuda de la API
            </div>
            
            <h2>🔗 Enlaces útiles:</h2>
            <p><a href="/status">Ver estado detallado</a></p>
            <p><a href="/help">Documentación de la API</a></p>
        </div>
    </body>
    </html>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route('/status')
def status():
    """Check bot status"""
    return jsonify({
        "status": "running",
        "bot_connected": bot_instance is not None,
        "google_sheets_connected": bot_instance.sheet is not None if bot_instance else False,
        "timestamp": datetime.now().isoformat(),
        "message": "Bot de gastos funcionando correctamente",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "development")
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
        expense_data = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'product': str(data['producto']),
            'place': str(data['lugar']),
            'category': str(data['categoria']),
            'subcategory': str(data['subcategoria']),
            'amount': float(data['importe']),
            'quantity': int(data['cantidad'])
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

@app.route('/health')
def health():
    """Simple health check for monitoring services"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/help')
def help_endpoint():
    """API help endpoint"""
    return jsonify({
        "endpoints": {
            "/": "Página principal con estado del bot",
            "/status": "Estado detallado del bot en JSON",
            "/health": "Health check simple",
            "/add_expense": "Agregar gasto (POST con datos JSON)",
            "/help": "Esta ayuda"
        },
        "add_expense_format": {
            "method": "POST",
            "content_type": "application/json",
            "body": {
                "producto": "Nombre del producto",
                "lugar": "Lugar de compra",
                "categoria": "Categoría",
                "subcategoria": "Subcategoría", 
                "importe": "Precio (número)",
                "cantidad": "Cantidad (número)"
            }
        },
        "example": {
            "producto": "Pan",
            "lugar": "Panadería",
            "categoria": "Comida",
            "subcategoria": "Productos básicos",
            "importe": 2500,
            "cantidad": 1
        }
    })

def set_bot_instance(bot):
    """Set the bot instance for API access"""
    global bot_instance
    bot_instance = bot

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
