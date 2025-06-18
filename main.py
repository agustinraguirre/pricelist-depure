import xmlrpc.client
from odoo_config import url, db, username, password

#Autenticacion
print("Conectando a Odoo...")
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
print("Autenticación exitosa.")

# Buscar la lista de precios
print("Buscando lista de precios...")
pricelist_id = models.execute_kw(db, uid, password,
    'product.pricelist', 'search',
    [[['id', '=', '202']]],
    {'limit': 1})[0]
print(f"Lista de precios encontrada: ID {pricelist_id}")

# Obtener líneas de la lista
print("Obteniendo reglas de precios...")
items = models.execute_kw(db, uid, password,
    'product.pricelist.item', 'search_read',
    [[['pricelist_id', '=', pricelist_id]]],
    {'fields': ['id', 'product_tmpl_id', 'fixed_price', 'create_date']})
print(f"Total de reglas encontradas: {len(items)}")

# Detectar duplicados
vistos = {}
duplicados = {}

for i, item in enumerate(items, 1):
    product = item.get('product_tmpl_id')
    create_date = item.get('create_date')

    if isinstance(product, list) and len(product) > 0:
        product_id = product[0]
        print(f"[{i}/{len(items)}] Procesando producto ID {product_id} - Fecha: {create_date}")
        if product_id in vistos:
            if create_date > vistos[product_id]['create_date']:
                duplicados.setdefault(product_id, []).append(vistos[product_id]['id'])
                vistos[product_id] = {'id': item['id'], 'create_date': create_date}
                print(f"  ↳ Duplicado detectado. Se conservará la regla más reciente.")
            else:
                duplicados.setdefault(product_id, []).append(item['id'])
                print(f"  ↳ Duplicado detectado. Se conservará la regla anterior.")
        else:
            vistos[product_id] = {'id': item['id'], 'create_date': create_date}

# Obtener SKUs
productos_eliminados = {product_id: len(ids) for product_id, ids in duplicados.items()}
skus = models.execute_kw(db, uid, password,
    'product.template', 'search_read',
    [[['id', 'in', list(productos_eliminados.keys())]]],
    {'fields': ['id', 'default_code']})
sku_map = {product['id']: product['default_code'] for product in skus}

# Eliminar duplicados
if duplicados:
    print("Eliminando reglas duplicadas...")
    total_eliminadas = 0
    for product_id, ids in duplicados.items():
        print(f" - Eliminando {len(ids)} reglas para producto ID {product_id} (SKU: {sku_map.get(product_id, 'Desconocido')})")
        models.execute_kw(db, uid, password,
            'product.pricelist.item', 'unlink',
            [ids])
        total_eliminadas += len(ids)
    print(f"✅ Se eliminaron {total_eliminadas} reglas duplicadas.")
    print("Productos afectados:")
    for product_id, count in productos_eliminados.items():
        print(f" - SKU: {sku_map.get(product_id, 'Desconocido')}, Reglas eliminadas: {count}")
else:
    print("✅ No se encontraron reglas duplicadas.")
