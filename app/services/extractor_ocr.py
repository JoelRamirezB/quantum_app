import pdfplumber
import pytesseract
from PIL import Image
import re 
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class ExtractorOCR:

    def procesar_pdf(self, ruta_archivo):
        texto = self._extraer_texto_pdfplumber(ruta_archivo)
        if not texto or len(texto.strip()) < 50 or '(cid:' in texto:
            texto = self._extraer_texto_ocr(ruta_archivo)
        cabecera = self._extraer_cabecera(texto)
        items = self._extraer_items(texto)
        return {'cabecera': cabecera, 'items': items, 'texto_crudo': texto}

    def _extraer_texto_pdfplumber(self, ruta_archivo):
        try:
            texto_completo = ''
            with pdfplumber.open(ruta_archivo) as pdf:
                for pagina in pdf.pages:
                    texto_pagina = pagina.extract_text()
                    if texto_pagina:
                        texto_completo += texto_pagina + '\n'
            return texto_completo
        except Exception as e:
            print(f'Error extrayendo texto con pdfplumber: {e}')
            return ''

    def _extraer_texto_ocr(self, ruta_archivo):
        try:
            texto_completo = ''
            with pdfplumber.open(ruta_archivo) as pdf:
                for pagina in pdf.pages:
                    imagen = pagina.to_image(resolution=300).original
                    texto_pagina = pytesseract.image_to_string(imagen, lang='spa')
                    texto_completo += texto_pagina + '\n'
            return texto_completo
        except Exception as e:
            print(f'Error extrayendo texto con OCR: {e}')
            return ''

    def _extraer_cabecera(self, texto):
        cabecera = {
            'numero_factura': None,
            'nit_proveedor': None,
            'proveedor': None,
            'fecha_emision': None,
        }
        if not texto:
            return cabecera

        cabecera['numero_factura'] = self._extraer_numero_factura(texto)
        cabecera['nit_proveedor'] = self._extraer_nit_proveedor(texto)
        cabecera['proveedor'] = self._extraer_proveedor(texto)
        cabecera['fecha_emision'] = self._extraer_fecha(texto)
        return cabecera
        
    def _extraer_numero_factura(self, texto):
        patrones = [
            r'(?:N[°º]|No\.?|Número|NUMERO|Factura|FACTURA)\s*[-:]?\s*([A-Z]{1,5}[-\s]?\d{4,10})',
            r'\b((?:FEIG|FE|CT|POE|FV|FC|FES|FAC|SFC)[-\s]?\d{3,10})\b',
            r'VENTA\s*:?\s*\n?\s*([A-Z]{1,5}[-\s]?\d{3,10})',
            r'CT\s+No\.?\s*(\d{3,6})',
            r'(?:ELECTR[ÓO]NICA\s+DE\s+VENTA|DE\s+VENTA)\s+([A-Z]{1,5}\d*\s*[-–]\s*\d{4,10})',
            r'(?:factura|FACTURA)[^\n]{0,50}([A-Z]{1,3}[-]?\d{4,10})',
        ]

        for patron in patrones:
            match = re.search(patron, texto, re.IGNORECASE | re.MULTILINE)
            if match:
                resultado = match.group(1).strip()
                if len(resultado) < 4:
                    continue
                if re.match(r'^\d{7,}$', resultado):
                    continue
                if re.match(r'^\d{2}/\d{2}/\d{4}$', resultado):
                    continue
                return resultado
        return None

    def _extraer_nit_proveedor(self, texto):
        lineas = texto.split('\n')

        patrones_nit = [
            r'(?:NIT|Nit|N\.I\.T)[:\s\.]*(\d{3}[,.]?\d{3}[,.]?\d{3}[-–\s]?\d)',
            r'(?:NIT|Nit|N\.I\.T)[:\s\.]*(\d{7,10}[-–]?\d?)',
        ]

        nits_encontrados = []
        for patron in patrones_nit:
            for match in re.finditer(patron, texto):
                nit = match.group(1).strip()
                nit_limpio = re.sub(r'[,.\s]', '', nit)
                pos = match.start()
                nits_encontrados.append((pos, nit_limpio))
        
        if not nits_encontrados:
            return None

        nits_encontrados.sort(key=lambda x: x[0])

        nit_atelcro = '9008889911'
        for pos, nit in nits_encontrados:
            nit_sin_digito = nit [:-1] if len(nit) > 9 else nit
            if '900888991' not in nit and '9008889911' not in nit:
                return nit
        return nits_encontrados[0][1] if nits_encontrados else None

    def _extraer_proveedor(self, texto):
        lineas = texto.split('\n')

        palabras_excluir = [
            'factura', 'electronica', 'electrónica', 'venta',
            'nit', 'fecha', 'cliente', 'señores', 'dirección',
            'telefono', 'teléfono', 'correo', 'email', 'pagina',
            'página', 'resolución', 'resolucion', 'autorizacion',
            'item', 'código', 'descripción', 'cantidad', 'valor',
            'subtotal', 'total', 'iva', 'representación'
        ]

        for linea in lineas[:8]:
            linea = linea.strip()
            if len(linea) < 5:
                continue
            if len(linea) > 100:
                continue
            linea_lower = linea.lower()
            if any(palabra in linea_lower for palabra in palabras_excluir):
                continue
            if re.match(r'^\d', linea):
                continue
            if re.match(r'^[A-ZÁÉÍÓÚÑ\s\.\,\-&]+$', linea, re.IGNORECASE):
                return linea
            if len(linea.split()) >= 2:
                return linea
        if lineas:
            return lineas[0].strip()[:100]

        return None

    def _extraer_fecha(self, texto):
        patrones_fecha = [
            r'(?:FECHA\s+(?:DE\s+)?(?:EMISI[ÓO]N|FACTURA|GENERACI[ÓO]N))[:\s]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'(?:Fecha\s+(?:y\s+Hora\s+de\s+)?(?:Emisión|Factura|Generación))[:\s]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'FECHA\s+FIRMADO[:\s]*(\d{2}/\d{2}/\d{4})',
            r'FECHA\s+DE\s+EMISI[ÓO]N.*?(\d{2})\s+(\d{2})\s+(\d{4})',
            r'(?:Generaci[oó]n|generaci[oó]n)[:\s]*(\d{4}-\d{2}-\d{2})',
            r'(?<!(?:vencimiento|VENCIMIENTO|vigencia|VIGENCIA)[^\n]{0,20})(\d{2}/\d{2}/\d{4})(?!\s*(?:vence|VENCE))',
        ]
        for patron in patrones_fecha:
            match = re.search(patron, texto, re.IGNORECASE | re.DOTALL)
            if match:
                if len(match.groups()) == 3:
                    dia = match.group(1)
                    mes = match.group(2)
                    anio = match.group(3)
                    return f'{dia}/{mes}/{anio}'
                else:
                    fecha = match.group(1).strip()
                    if re.match(r'\d{4}-\d{2}-\d{2}', fecha):
                        partes = fecha.split('-')
                        return f'{partes[2]}/{partes[1]}/{partes[0]}'
                    return fecha
        return None
    
    def _limpiar_numero(self, valor_texto):
        try:
            valor_texto = valor_texto.strip().replace('$', '').strip()
            
            if re.match(r'^\d{1,3}(,\d{3})*\.\d+$', valor_texto):
                return float(valor_texto.replace(',', ''))
            if re.match(r'^\d{1,3}(\.\d{3})*,\d+$', valor_texto):
                return float(valor_texto.replace('.', '').replace(',', '.'))
            if re.match(r'^\d{1,3}(\.\d{3})+$', valor_texto):
                return float(valor_texto.replace('.', ''))
            if re.match(r'^\d{1,3}(,\d{3})+$', valor_texto):
                return float(valor_texto.replace(',', ''))

            return float(valor_texto.replace(',', '.'))
            
        except Exception:
            return None

    def _extraer_items(self, texto):
        items = []

        if not texto:
            return items

        items = self._extraer_items_formato_imgh(texto)
        if not items:
            items = self._extraer_items_formato_tabla(texto)
        if not items:
            items = self._extraer_items_formato_pos(texto)
        return items
        
    def _extraer_items_formato_imgh(self, texto):
        items = []

        patron_item = re.compile(
            r'(\d+)\s+'
            r'(\d{8})\s+'
            r'(.+?)\s+'
            r'NAR\s+'
            r'(\d+(?:[.,]\d+)?),00\s+'
            r'\$([0-9.,]+)\s+'
            r'IVA\s+19%\s+\$([0-9.,]+)\s+'
            r'[\d.,]+\s+'
            r'\$([0-9.,]+)',
            re.DOTALL
        )
        
        matches = list(patron_item.finditer(texto))

        for i, match in enumerate(matches):
            try:
                descripcion = match.group(3).strip()
                descripcion = re.sub(r'\s-', ' ', descripcion)

                pos_fin = match.end()
                if i + 1 < len(matches):
                    texto_entre = texto[pos_fin:matches[i+1].start()]
                else:
                    pos_notas = texto.find('Notas:', pos_fin)
                    pos_son = texto.find('SON:', pos_fin)
                    pos_fin_seccion = min(p for p in [pos_notas, pos_son, len(texto)] if p > 0)
                    texto_entre = texto[pos_fin:pos_fin_seccion]

                lineas_extra = texto_entre.strip().split('\n')
                descripcion_extra = ''
                for linea in lineas_extra:
                    linea = linea.strip()
                    if re.match(r'^\d{2}\s+', linea):
                        contenido = re.sub(r'^\d{2}\s+', '', linea).strip()
                        if contenido and not re.match(r'^\d{8}', contenido):
                            descripcion_extra += ' ' + contenido
                            
                descripcion_completa = re.sub(r'\s+', ' ', (descripcion + descripcion_extra).strip())
                cantidad = float(match.group(4).replace(',', '.'))
                valor_unitario = self._limpiar_numero(match.group(5))

                item = {
                    'codigo_producto': match.group(2).strip(),
                    'descripcion': descripcion_completa,
                    'cantidad': cantidad,
                    'valor_unitario': valor_unitario or 0.0,
                    'porcentaje_impuesto': 19.0
                }
                items.append(item)

            except Exception as e:
                print(f'Error procesando item IMGH: {e}')
                continue

        return items
    
    def _extraer_items_formato_tabla(self, texto):
        items = []

        patrones_inicio = [
            r'(?:Item|ITEM|N[°º]|#)\s+(?:C[oó]digo|COD|SKU)?\s*(?:Descripci[oó]n|DESCRIPCI[ÓO]N)',
            r'(?:Item|ITEM|N[°º])\s+(?:Descripci[oó]n|DESCRIPCI[ÓO]N)',
        ]

        inicio_tabla = -1
        for patron in patrones_inicio:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                inicio_tabla = match.end()
                break

        if inicio_tabla == -1:
            return items

        texto_tabla = texto[inicio_tabla:]

        fin_tabla_patrones = [
            r'(?:Item|ITEM|N[°º]|#)\s+(?:C[oó]digo|COD|SKU)?\s*(?:Descripci[oó]n|DESCRIPCI[ÓO]N)',
            r'(?:Item|ITEM|N[°º])\s+(?:Descripci[oó]n|DESCRIPCI[ÓO]N)',
        ]
        for patron in fin_tabla_patrones:
            match = re.search(patron, texto_tabla, re.IGNORECASE)
            if match:
                texto_tabla = texto_tabla[:match.start()]
                break
        
        patron_linea = re.compile(
            r'(\d+)\s+'
            r'([A-Z0-9\-\.]+)\s+'
            r'(.+?)\s+'
            r'(\d+(?:[.,]\d+)?)\s+'
            r'(?:Und\.?|UND\.?|unid\.?|und\.?|M\.?|MTS\.?|KG\.?)?\s*'
            r'([0-9.,]+)\s+'
            r'(?:\d+[,.]?\d*%?\s+)?'
            r'(?:[0-9.,]+\s+)?'
            r'([0-9.,]+)\s*$',
            re.MULTILINE
        )

        for match in patron_linea.finditer(texto_tabla):
            try:
                descripcion = match.group(3).strip()
                descripcion = re.sub(r'\s+', ' ', descripcion)
                cantidad = self._limpiar_numero(match.group(4))
                valor_unitario = self._limpiar_numero(match.group(5))

                if not cantidad or not valor_unitario:
                    continue

                item = {
                    'codigo_producto': match.group(2).strip(),
                    'descripcion': descripcion,
                    'cantidad': cantidad,
                    'valor_unitario': valor_unitario,
                    'porcentaje_impuesto': 19.0
                }
                items.append(item)

            except Exception as e:
                print(f'Error procesando item tabla: {e}')
                continue
        
        return items
    
    def _extraer_items_formato_pos(self, texto):
        items = []

        patron = re.compile(
            r'(\d+)\s+'
            r'(.+?)\s+'
            r'(?:Und\.?|UND|unid\.?|UDM)\s+'    
            r'([\d.,]+)\s+'
            r'\$?\s*([\d,\.]+)\s+'
            r'IVA\s+([\d]+(?:[.,]\d+)?)%',
            re.MULTILINE
        )

        for match in patron.finditer(texto):
            try:
                descripcion = match.group(2).strip()
                cantidad_texto = match.group(3)
                cantidad = self._limpiar_numero(cantidad_texto)
                valor_unitario = self._limpiar_numero(match.group(4))
                porcentaje_texto = match.group(5).replace(',', '.')
                porcentaje = float(porcentaje_texto)

                if not cantidad or not valor_unitario:
                    continue

                if cantidad > 10000:
                    cantidad = cantidad / 1000
                if porcentaje > 100:
                    porcentaje = porcentaje / 100

                item = {
                    'codigo_producto': '',
                    'descripcion': descripcion,
                    'cantidad': cantidad,
                    'valor_unitario': valor_unitario,
                    'porcentaje_impuesto': porcentaje
                }
                items.append(item)

            except Exception as e:
                print(f'Error procesando item POS: {e}')
                continue

        return items
