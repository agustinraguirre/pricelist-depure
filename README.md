# pricelist-depure
Script en Python que se conecta a una instancia de Odoo mediante XML-RPC para depurar listas de precios. Elimina reglas de precios duplicadas por producto, conservando únicamente la más reciente según la fecha de creación (create_date). Muestra en consola el SKU de cada producto afectado y la cantidad de reglas eliminadas.
