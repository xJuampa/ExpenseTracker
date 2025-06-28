# Bot de Gastos - Funcionando

Tu bot está conectado a la hoja "Gastos" y operativo.

## Formato de mensaje:
```
Producto
Lugar  
Categoría
Subcategoría
Importe
Cantidad
```

**Ejemplo:**
```
Pan
Panadería
Comida
Productos básicos
2500
1
```

El bot registra automáticamente la fecha en tu hoja.

## API Web disponible:
Tu bot ahora expone una API en el puerto 8080 que permite a otras aplicaciones web agregar gastos directamente.

**Endpoint principal:**
```
POST /add_expense
Content-Type: application/json
```

Ejemplo de uso desde otra aplicación:
```javascript
fetch('https://expensetracker.forkydrive.replit.app/add_expense', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    producto: "Almuerzo",
    lugar: "Restaurante", 
    categoria: "Comida",
    subcategoria: "Almuerzo",
    importe: "12000",
    cantidad: "1"
  })
})
```

Ver archivo `api_examples.md` para más detalles.