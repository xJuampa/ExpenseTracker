# Cómo compartir tu hoja "Gastos" con el bot

Para que el bot pueda acceder a tu hoja "Gastos" existente, necesitas compartirla con la cuenta de servicio de Google:

## Email de la cuenta de servicio:
**gastos-bot@bottelegramgastos-463810.iam.gserviceaccount.com**

## Pasos:

1. **Compartir tu hoja "Gastos":**
   - Abre tu hoja "Gastos" en Google Sheets
   - Haz clic en el botón "Compartir" (esquina superior derecha)
   - Pega este email: `gastos-bot@bottelegramgastos-463810.iam.gserviceaccount.com`
   - Dale permisos de "Editor"
   - Haz clic en "Enviar"

2. **Probar el bot:**
   - Una vez compartida, el bot podrá encontrar y usar tu hoja existente
   - Envía un mensaje de prueba al bot con 5 líneas

## Formato del mensaje para el bot:
```
Producto
Lugar
Categoría
Subcategoría
Importe
```

Ejemplo:
```
Pan
Panadería
Comida
Productos básicos
2500
```

El bot registrará automáticamente la fecha y cantidad (1 por defecto) en tu hoja.

## Importante:
- El bot buscará tu hoja "Gastos" una vez que la hayas compartido
- Si el bot sigue sin encontrarla, reinicia el bot enviando cualquier mensaje
- Los datos se guardarán en las columnas que ya tienes configuradas