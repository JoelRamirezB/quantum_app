import requests
from flask import current_app
from datetime import date

class SiigoService:

    def __init__(self):
        self.token = None
        self.url_base = None

    def _obtener_headers(self):
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Partner-Id': 'QuantumAtelcro'
        }

    def obtener_token(self):
        try:
            url_base = current_app.config.get(
                'SIIGO_URL', 'https://api.siigo.com')
            usuario = current_app.config.get('SIIGO_USUARIO')
            llave = current_app.config.get('SIIGO_LLAVE_ACCESO')

            url = f'{url_base}/auth'
            headers = {
                'Content-Type': 'application/json',
                'Partner-Id': 'QuantumAtelcro'
            }
            body = {
                'username': usuario,
                'access_key': llave
            }
            respuesta = requests.post(
                url, json=body, headers=headers)

            if respuesta.status_code == 200:
                datos = respuesta.json()
                self.token = datos.get('access_token')
                self.url_base = url_base
                return self.token
            else:
                print(f'Error token: {respuesta.status_code} '
                      f'{respuesta.text}')
                return None

        except Exception as e:
            print(f'Error conexion SIIGO: {str(e)}')
            return None

    def obtener_tipos_comprobante(self):
        if not self.token:
            self.obtener_token()
        if not self.token:
            return None
        try:
            url = f'{self.url_base}/v1/document-types?type=FV'
            respuesta = requests.get(
                url, headers=self._obtener_headers())
            if respuesta.status_code == 200:
                return respuesta.json()
            print(f'Error comprobantes: {respuesta.text}')
            return None
        except Exception as e:
            print(f'Error: {str(e)}')
            return None

    def obtener_usuarios(self):
        if not self.token:
            self.obtener_token()
        if not self.token:
            return None
        try:
            url = f'{self.url_base}/v1/users'
            respuesta = requests.get(
                url, headers=self._obtener_headers())
            if respuesta.status_code == 200:
                datos = respuesta.json()
                if isinstance(datos, list):
                    return datos
                return datos.get('results', [])
            print(f'Error usuarios: {respuesta.text}')
            return None
        except Exception as e:
            print(f'Error: {str(e)}')
            return None

    def obtener_impuestos(self):
        if not self.token:
            self.obtener_token()
        if not self.token:
            return None
        try:
            url = f'{self.url_base}/v1/taxes'
            respuesta = requests.get(
                url, headers=self._obtener_headers())
            if respuesta.status_code == 200:
                datos = respuesta.json()
                if isinstance(datos, list):
                    return datos
                return datos.get('results', [])
            print(f'Error impuestos: {respuesta.text}')
            return None
        except Exception as e:
            print(f'Error: {str(e)}')
            return None

    def obtener_formas_pago(self):
        if not self.token:
            self.obtener_token()
        if not self.token:
            return None
        try:
            url = (f'{self.url_base}/v1/payment-types'
                   f'?document_type=FV')
            respuesta = requests.get(
                url, headers=self._obtener_headers())
            if respuesta.status_code == 200:
                datos = respuesta.json()
                if isinstance(datos, list):
                    return datos
                return datos.get('results', [])
            print(f'Error formas pago: {respuesta.text}')
            return None
        except Exception as e:
            print(f'Error: {str(e)}')
            return None

    def obtener_productos(self):
        if not self.token:
            self.obtener_token()
        if not self.token:
            return None
        try:
            url = f'{self.url_base}/v1/products?page=1&page_size=5'
            respuesta = requests.get(
                url, headers=self._obtener_headers())
            print(f'Productos raw: {respuesta.text[:800]}')
            if respuesta.status_code == 200:
                datos = respuesta.json()
                if isinstance(datos, list):
                    return datos
                return datos.get('results', [])
            print(f'Error productos: {respuesta.text}')
            return None
        except Exception as e:
            print(f'Error: {str(e)}')
            return None

    def obtener_consecutivo(self, id_comprobante):
        if not self.token:
            self.obtener_token()
        if not self.token:
            return None
        try:
            url = (f'{self.url_base}/v1/document-types'
                f'?type=FV')
            respuesta = requests.get(
                url, headers=self._obtener_headers())
            if respuesta.status_code == 200:
                comprobantes = respuesta.json()
                for comp in comprobantes:
                    if comp.get('id') == id_comprobante:
                        consecutivo = comp.get('consecutive', 0)
                        print(f'Consecutivo actual: {consecutivo}')
                        return consecutivo + 1
            return None
        except Exception as e:
            print(f'Error: {str(e)}')
            return None

    def obtener_ultimo_consecutivo(self, id_comprobante):
        if not self.token:
            self.obtener_token()
        if not self.token:
            return 200
        try:
            url = (f'{self.url_base}/v1/invoices'
                f'?document_id={id_comprobante}'
                f'&page=1&page_size=25'
                f'&date_start=2020-01-01'
                f'&date_end=2026-12-31')
            respuesta = requests.get(
                url, headers=self._obtener_headers())
            if respuesta.status_code == 200:
                datos = respuesta.json()
                resultados = datos.get('results', [])
                if resultados:
                    numeros = []
                    for r in resultados:
                        num = r.get('number', 0)
                        if isinstance(num, int):
                            numeros.append(num)
                    if numeros:
                        siguiente = max(numeros) + 1
                        print(f'Ultimo consecutivo: {max(numeros)}'
                            f' - Siguiente: {siguiente}')
                        return siguiente
            return 200
        except Exception as e:
            print(f'Error: {str(e)}')
            return 200

    def construir_json_factura(self, factura):
        items = []
        for item in factura.items:
        
            id_impuesto = 5268 if float(
                item.porcentaje_impuesto or 0) == 19 else 49162

            descripcion_lower = (item.descripcion or '').lower()
            if any(p in descripcion_lower for p in [
                    'mecanizado', 'servicio', 'mano de obra',
                    'instalacion', 'mantenimiento', 'reparacion',
                    'fabricacion', 'suministro', 'asesor']):
                codigo = 'SE-001'
            else:
                codigo = 'MT1'

            items.append({
                'code': codigo,
                'description': (item.descripcion
                                or 'Sin descripcion')[:200],
                'quantity': float(item.cantidad or 1),
                'price': float(item.valor_unitario or 0),
                'discount': 0,
                'taxes': [{'id': id_impuesto}]
            })

        metodo_pago = factura.metodo_pago or 'Credito'
        if ('contado' in metodo_pago.lower() or
                'efectivo' in metodo_pago.lower()):
            id_forma_pago = 2299
        else:
            id_forma_pago = 2300

        if factura.fecha_emision:
            fecha_str = factura.fecha_emision.strftime(
                '%Y-%m-%d')
        else:
            fecha_str = date.today().strftime('%Y-%m-%d')

        nit_limpio = str(
            factura.nit_proveedor or '').replace(
            '-', '').replace('.', '').replace(  
            ',', '').strip()

        consecutivo = self.obtener_ultimo_consecutivo(49591)
        print(f'Siguiente consecutivo: {consecutivo}')  

        json_factura = {
            'document': {'id': 49591},
            'number': consecutivo,
            'date': fecha_str,
            'customer': {
                'person_type': 'Company',
                'id_type': '31',
                'identification': nit_limpio,
                'name': [(factura.proveedor or 'Sin nombre')[:100]],
                'branch_office': 0,
                'address': {
                    'address': 'Sin direccion',
                    'city': {
                        'country_code': 'Co',
                        'state_code': '11',
                        'city_code': '11001'
                    }
                },
                'contacts': []
            },
            
            'seller': 725,
            'observations': f'Factura {factura.numero_factura}',
            'items': items,
            'payments': [{
                'id': id_forma_pago,
                'value': float(factura.total_pagar or 0),
                'due_date': fecha_str
            }]
        }

        return json_factura

    def registrar_factura(self, json_factura):
        if not self.token:
            self.obtener_token()
        if not self.token:
            return None
        try:
            url = f'{self.url_base}/v1/invoices'
            respuesta = requests.post(
                url,
                json=json_factura,
                headers=self._obtener_headers())
            print(f'Status: {respuesta.status_code}')
            print(f'Respuesta: {respuesta.text}')
            if respuesta.status_code in [200, 201]:
                return respuesta.json()
            return None
        except Exception as e:
            print(f'Error: {str(e)}')
            return None