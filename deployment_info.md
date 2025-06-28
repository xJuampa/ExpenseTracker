# Deployment del Bot de Gastos

## Estado actual:
✅ Bot de Telegram funcionando
✅ API web operativa en puerto 8080
✅ Google Sheets conectado
✅ Keep-alive server activo
✅ Listo para deployment

## Pasos para deployment:
1. **En Replit, busca el botón "Deploy"** (generalmente en la parte superior)
2. **Haz clic en "Deploy"** para iniciar el proceso
3. **Espera a que termine** el proceso de deployment
4. **Obtén la URL pública** que te proporciona Replit

## Una vez desplegado:
Tu URL pública será algo como:
- `https://tu-proyecto.replit.app/` - Para verificar estado
- `https://tu-proyecto.replit.app/status` - Para detalles del bot
- `https://tu-proyecto.replit.app/add_expense` - Para API de gastos

## Verificación post-deployment:
```bash
# Probar el endpoint de estado
curl https://tu-url-publica.replit.app/

# Debería responder: "Bot is alive!"
```

## Notas importantes:
- El deployment maneja automáticamente la exposición del puerto
- La URL será estable y accesible desde cualquier lugar
- Tanto el bot de Telegram como la API web funcionarán simultáneamente
- Replit Deployments incluye TLS automático y health checks

Tu proyecto está completamente preparado para el deployment.