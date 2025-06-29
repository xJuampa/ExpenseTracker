#!/usr/bin/env python3
"""
Script de prueba para verificar la configuración local del bot
"""
import os
import json
from datetime import datetime

def test_environment():
    """Test environment variables"""
    print("🔍 Verificando variables de entorno...")
    
    bot_token = os.getenv("BOT_TOKEN")
    google_creds = os.getenv("GOOGLE_CREDS")
    
    if bot_token:
        print("✅ BOT_TOKEN encontrado")
    else:
        print("❌ BOT_TOKEN no encontrado")
    
    if google_creds:
        try:
            json.loads(google_creds)
            print("✅ GOOGLE_CREDS es un JSON válido")
        except json.JSONDecodeError:
            print("❌ GOOGLE_CREDS no es un JSON válido")
    else:
        print("❌ GOOGLE_CREDS no encontrado")

def test_imports():
    """Test if all required packages can be imported"""
    print("\n📦 Verificando imports...")
    
    try:
        import flask
        print("✅ Flask importado correctamente")
    except ImportError:
        print("❌ Flask no se puede importar")
    
    try:
        import gspread
        print("✅ gspread importado correctamente")
    except ImportError:
        print("❌ gspread no se puede importar")
    
    try:
        import telegram
        print("✅ python-telegram-bot importado correctamente")
    except ImportError:
        print("❌ python-telegram-bot no se puede importar")
    
    try:
        from oauth2client.service_account import ServiceAccountCredentials
        print("✅ oauth2client importado correctamente")
    except ImportError:
        print("❌ oauth2client no se puede importar")

def test_keep_alive():
    """Test keep_alive module"""
    print("\n🌐 Verificando keep_alive...")
    
    try:
        from keep_alive import app
        print("✅ Flask app creado correctamente")
        
        # Test basic routes
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Endpoint / funciona correctamente")
            else:
                print(f"❌ Endpoint / devuelve {response.status_code}")
            
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ Endpoint /health funciona correctamente")
            else:
                print(f"❌ Endpoint /health devuelve {response.status_code}")
                
    except Exception as e:
        print(f"❌ Error en keep_alive: {e}")

def main():
    """Run all tests"""
    print("🚀 Iniciando pruebas del Bot de Gastos")
    print("=" * 50)
    
    test_environment()
    test_imports()
    test_keep_alive()
    
    print("\n" + "=" * 50)
    print("✅ Pruebas completadas")
    print("\n📝 Para ejecutar el bot:")
    print("   python expense_bot.py")
    print("\n📝 Para probar solo la API:")
    print("   python -c \"from keep_alive import app; app.run(debug=True)\"")

if __name__ == "__main__":
    main() 