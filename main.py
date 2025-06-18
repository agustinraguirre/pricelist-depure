import xmlrpc.client
from config import url, db, username, password

def conectar_odoo():
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    return uid, models

def obtener_items(models, uid, pricelist_id):
    return models.execute_kw(db, uid, password,
        'product.pricelist.item', 'search_read',
        [[['pricelist_id', '=', pricelist_id]]],
        {'fields': ['id', 'product_tmpl_id', 'fixed_price', 'create_date']})

def detectar_duplicados(items):
    vistos = {}
    duplicados = {}

    for item in items:
        product = item.get('product_tmpl_id')
        create_date = item.get('create_date')

        if isinstance(product, list) and len(product) > 0:
            product_id = product[0]
            if product_id in vistos:
                if create_date > vistos[product_id]['create_date']:
                    duplicados.setdefault(product_id, []).append(vistos[product_id]['id'])
                    vistos[product_id] = {'id': item['id'], 'create_date': create_date}
                else:
                    duplicados.setdefault(product_id, []).append(item['id'])
            else:
                vistos[product_id] = {'id': item['id'], 'create_date': create_date}
    return duplicados

def obtener_skus(models, uid, product_ids):
    skus = models.execute_kw(db, uid, password,
        'product.template', 'search_read',
        [[['id', 'in', product_ids]]],
        {'fields': ['id', 'default_code']})
    return {product['id']: product['default_code'] for product in skus}

def eliminar_duplicados(models, uid, duplicados, sku_map):
    total = 0
    for product_id, ids in duplicados.items():
        models.execute_kw(db, uid, password,
            'product.pricelist.item', 'unlink',
            [ids])
        total += len(ids)
        print(f" - SKU: {sku_map.get(product_id, 'Desconocido')}, Reglas eliminadas: {len(ids)}")
    print(f"\nSe eliminaron {total} registros duplicados.")

def main():
    uid, models = conectar_odoo()

    pricelist_id = models.execute_kw(db, uid, password,
        'product.pricelist', 'search',
        [[['id', '=', 201]]], {'limit': 1})[0]

    items = obtener_items(models, uid, pricelist_id)
    duplicados = detectar_duplicados(items)

    if duplicados:
        sku_map = obtener_skus(models, uid, list(duplicados.keys()))
        eliminar_duplicados(models, uid, duplicados, sku_map)
    else:
        print("No se encontraron registros duplicados.")

if __name__ == "__main__":
    main()
