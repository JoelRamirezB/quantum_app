from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.services.siigo_service import SiigoService

app = create_app()

with app.app_context():
    siigo = SiigoService()
    print('Métodos disponibles:', [m for m in dir(siigo) if not m.startswith('_')])

    print('1. Obteniendo token...')
    token = siigo.obtener_token()
    if not token:
        print('ERROR: No se pudo obtener el token')
        exit()
    print(f'Token: OK')

    print('\n2. Obteniendo comprobantes...')
    comprobantes = siigo.obtener_tipos_comprobante()
    if comprobantes:
        for comp in comprobantes:
            if isinstance(comp, dict):
                print(f'  ID: {comp.get("id")} | '
                      f'Nombre: {comp.get("name")}')

    print('\n3. Obteniendo usuarios...')
    usuarios = siigo.obtener_usuarios()
    if usuarios:
        for user in usuarios:
            if isinstance(user, dict):
                print(f'  ID: {user.get("id")} | '
                      f'Nombre: {user.get("first_name")} '
                      f'{user.get("last_name")}')

    print('\n4. Obteniendo impuestos...')
    impuestos = siigo.obtener_impuestos()
    if impuestos:
        for imp in impuestos:
            if isinstance(imp, dict):
                print(f'  ID: {imp.get("id")} | '
                      f'Nombre: {imp.get("name")} | '
                      f'Porcentaje: {imp.get("percentage")}')

    print('\n5. Obteniendo formas de pago...')
    formas_pago = siigo.obtener_formas_pago()
    if formas_pago:
        for fp in formas_pago:
            if isinstance(fp, dict):
                print(f'  ID: {fp.get("id")} | '
                      f'Nombre: {fp.get("name")}')
    else:
        print('No se pudieron obtener formas de pago')

    print('\n6. Probando construccion de JSON con factura real...')
    from app.models import Factura
    factura = Factura.query.filter_by(
        estado='VALIDADA').first()

    if factura:
        print(f'Factura encontrada: {factura.numero_factura}')
        json_factura = siigo.construir_json_factura(factura)
        import json
        print('JSON construido:')
        print(json.dumps(json_factura, indent=2, 
                        ensure_ascii=False))
    else:
        print('No hay facturas validadas para probar')

    print('\n6b. Obteniendo productos de SIIGO...')
    productos = siigo.obtener_productos()
    if productos:
        for prod in productos:
            if isinstance(prod, dict):
                print(f'  Codigo: {prod.get("code")} | '
                    f'Nombre: {prod.get("name")}')

    print('\n7. Enviando factura a SIIGO...')
    from app.models import Factura
    factura = Factura.query.filter(
        Factura.numero_factura == 'FEIG1593'
    ).first()

    if not factura:
        factura = Factura.query.filter(
            Factura.nit_proveedor != 'POR_REVISAR',
            Factura.items.any()
        ).first()

    print('\n6c. Consultando consecutivos usados...')
    consecutivos = siigo.obtener_ultimo_consecutivo(49591)
    print(f'Resultado: {consecutivos}')

    if factura:
        json_factura = siigo.construir_json_factura(factura)
        import json
        print('JSON a enviar:')
        print(json.dumps(json_factura, indent=2, ensure_ascii=False))
        respuesta = siigo.registrar_factura(json_factura)
        if respuesta:
            print(f'Exito: {respuesta}')
        else:
            print('Error al registrar')
    else:
        print('No hay facturas')

    print('\n=== FIN DIAGNÓSTICO ===')