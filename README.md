# 🧹 Pricelist Depure para Odoo

Este script en Python se conecta a una instancia de Odoo mediante XML-RPC y limpia reglas de precios duplicadas en una lista específica, conservando únicamente la más reciente por producto.

---

## 🚀 ¿Qué hace?

- Se conecta a tu servidor Odoo.
- Busca una lista de precios específica.
- Detecta reglas duplicadas por producto.
- Elimina todas las reglas duplicadas, dejando solo la más reciente.
- Muestra los SKUs afectados y la cantidad de reglas eliminadas.

---

## 🛠️ Requisitos

- Python 3.7 o superior
- Acceso a una instancia de Odoo con XML-RPC habilitado
