# API del Bot de Gastos

Tu bot ahora expone una API web que permite a otras aplicaciones interactuar con él.

## Endpoints disponibles:

### 1. Verificar estado
```
GET /
Respuesta: "Bot is alive!"
```

### 2. Estado del bot
```
GET /status
Respuesta JSON con el estado del bot
```

### 3. Agregar gasto
```
POST /add_expense
Content-Type: application/json

Body:
{
  "producto": "Pan",
  "lugar": "Panadería", 
  "categoria": "Comida",
  "subcategoria": "Productos básicos",
  "importe": "2500",
  "cantidad": "1"
}
```

### 4. Ayuda
```
GET /help
Respuesta JSON con documentación de la API
```

## Ejemplo de uso con curl:

```bash
# Verificar estado
curl https://tu-replit-url.replit.app/status

# Agregar gasto
curl -X POST https://tu-replit-url.replit.app/add_expense \
  -H "Content-Type: application/json" \
  -d '{
    "producto": "Café",
    "lugar": "Cafetería Central",
    "categoria": "Bebidas",
    "subcategoria": "Café",
    "importe": "3500",
    "cantidad": "1"
  }'
```

## Desde JavaScript:

```javascript
// Agregar gasto
fetch('https://tu-replit-url.replit.app/add_expense', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    producto: "Almuerzo",
    lugar: "Restaurante XYZ",
    categoria: "Comida",
    subcategoria: "Almuerzo",
    importe: "12000",
    cantidad: "1"
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

La API registra los gastos directamente en tu hoja "Gastos" de Google Sheets, igual que el bot de Telegram.