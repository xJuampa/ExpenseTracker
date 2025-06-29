# 🤖 Bot de Gastos para Telegram

Bot de Telegram que registra gastos automáticamente en Google Sheets con API REST para monitoreo.

## 🚀 Deployment en Railway

### Paso 1: Preparar el repositorio

1. Sube tu código a GitHub
2. Asegúrate de que todos los archivos estén en la carpeta `ExpenseTracker/`

### Paso 2: Configurar Railway

1. Ve a [Railway.app](https://railway.app) y crea una cuenta
2. Haz clic en "New Project" → "Deploy from GitHub repo"
3. Selecciona tu repositorio
4. En la configuración del proyecto:
   - **Root Directory**: `ExpenseTracker`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python expense_bot.py`

### Paso 3: Configurar Variables de Entorno

En Railway, ve a la pestaña "Variables" y agrega:

```
BOT_TOKEN=tu_token_de_telegram
GOOGLE_CREDS={"type": "service_account", ...}
```

#### Obtener BOT_TOKEN:
1. Habla con [@BotFather](https://t.me/botfather) en Telegram
2. Crea un nuevo bot con `/newbot`
3. Copia el token que te da

#### Obtener GOOGLE_CREDS:
1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Crea un proyecto nuevo
3. Habilita Google Sheets API
4. Crea una cuenta de servicio
5. Descarga el JSON de credenciales
6. Copia todo el contenido del JSON como valor de `GOOGLE_CREDS`

### Paso 4: Deploy

1. Railway detectará automáticamente los cambios
2. El bot se desplegará en unos minutos
3. Obtendrás una URL como: `https://tu-proyecto.railway.app`

## 📡 Endpoints de la API

Una vez desplegado, tendrás acceso a:

- **`/`** - Página principal con estado del bot
- **`/status`** - Estado detallado en JSON
- **`/health`** - Health check simple
- **`/add_expense`** - Agregar gasto via API (POST)
- **`/help`** - Documentación de la API

## 🔧 Uso del Bot

### Via Telegram:
Envía un mensaje con exactamente 6 líneas:
```
Producto
Lugar
Categoría
Subcategoría
Importe
Cantidad
```

### Via API:
```bash
curl -X POST https://tu-proyecto.railway.app/add_expense \
  -H "Content-Type: application/json" \
  -d '{
    "producto": "Pan",
    "lugar": "Panadería",
    "categoria": "Comida",
    "subcategoria": "Productos básicos",
    "importe": 2500,
    "cantidad": 1
  }'
```

## 📊 Monitoreo

- **Uptime Robot**: Configura un monitor en `/health`
- **Railway Dashboard**: Monitorea logs y métricas
- **Google Sheets**: Verifica que los datos se registren correctamente

## 🛠️ Estructura del Proyecto

```
ExpenseTracker/
├── expense_bot.py      # Bot principal
├── keep_alive.py       # API REST y keep-alive
├── requirements.txt    # Dependencias
├── Procfile           # Configuración Railway
├── runtime.txt        # Versión de Python
└── start.sh          # Script de inicio
```

## 🔍 Troubleshooting

### Bot no responde:
1. Verifica `/status` en la URL de Railway
2. Revisa los logs en Railway Dashboard
3. Confirma que `BOT_TOKEN` esté correcto

### Error en Google Sheets:
1. Verifica que `GOOGLE_CREDS` sea un JSON válido
2. Confirma que la cuenta de servicio tenga permisos
3. Revisa que la API esté habilitada

### Deployment falla:
1. Verifica que `requirements.txt` esté en la raíz
2. Confirma que el directorio raíz sea `ExpenseTracker`
3. Revisa los logs de build en Railway

## 💰 Costos

- **Railway**: Gratis hasta 500 horas/mes
- **Google Sheets**: Gratis
- **Telegram Bot API**: Gratis

## 🆘 Soporte

Si tienes problemas:
1. Revisa los logs en Railway
2. Verifica las variables de entorno
3. Confirma que todos los archivos estén en el lugar correcto 