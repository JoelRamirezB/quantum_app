import pdfplumber
import pytesseract
from PIL import Image
import re 
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class ExtractorOCR:

    def procesar_pdf(self, ruta_archivo):
        texto = self._extraer_texto_pdfplumber(ruta_archivo)
        if not texto or len(texto.strip()) < 50:
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

        patrones_factura = [
            r'(FEIG\d+)',
            r'FACTURA ELECTR[ÓO]NICA DE\s*\n\s*([A-Z0-9]+)',
            r'VENTA\s*:\s*\n?\s*([A-Z]{2,}[0-9]+)',
            r'(?:No\.|Número|NUMERO)\s*[:\s#]*([A-Z]{2,}[0-9]+)',
            r'(?:Factura|FACTURA|FV|FE|No\.?|Número|NUMERO)[:\s#]*([A-Z0-9\-]+)',
            r'(?:Factura electrónica|FACTURA ELECTRÓNICA)[:\s#]*([A-Z0-9\-]+)',
            r'FACTURA ELECTR[ÓO]NICA DE\s+VENTA\s*:\*([A-Z0-9\-]+)',
            r'VENTA\s*:\s*([A-Z0-9\-]+)',
        ]
        for patron in patrones_factura:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                cabecera['numero_factura'] = match.group(1).strip()
                break

        patrones_nit = [
            r'NIT[:\s]*(\d{7,10}[--]?\d?)',
            r'Nit[:\s]*(\d{7,10}[--]?\d?)',
            r'N\.I\.T[:\s]*(\d{7,10}[--]?\d?)'
        ]
        for patron in patrones_nit:
            match = re.search(patron, texto)
            if match:
                cabecera['nit_proveedor'] = match.group(1).strip()
                break

        lineas = texto.split('\n')
        if lineas:
            primera_linea = lineas[0].strip()
            if len(primera_linea) > 5:
                cabecera['proveedor'] = primera_linea

        patrones_fecha = [
            r'(?:Fecha|FECHA)[:\s]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
            r'FECHA DE EMISO[ÓO]N.*?(\d{2})\s+(\d{2})\s+(\d{4})',
            r'FECHA FIRMADO[:\s]*(\d{2}/\d{2}/\d{4})',
            r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})'
        ]
        for patron in patrones_fecha:
            match = re.search(patron, texto)
            if match:
                if len(match.groups()) == 3:
                    dia = match.group(1)
                    mes = match.group(2)
                    anio = match.group(3)
                    cabecera['fecha_emision'] = f'{dia}/{mes}/{anio}'
                else:
                    cabecera['fecha_emision'] = match.group(1).strip()
                break
    
        return cabecera

    def _limpiar_numero(self, valor_texto):
        try:
            limpio = valor_texto.replace('.', '').replace(',', '.')
            return float(limpio)
        except Exception:
            return None

    def _extraer_items(self, texto):
        items = []
        if not texto:
            return items

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
        

        for match in patron_item.finditer(texto):
            try:
                descripcion = match.group(3).strip()
                descripcion = re.sub(r'\s+', ' ', descripcion)
                cantidad = float(match.group(4).replace(',', '.'))
                valor_unitario = self._limpiar_numero(match.group(5))

                item = {
                    'codigo_producto': match.group(2).strip(),
                    'descripcion': descripcion,
                    'cantidad': cantidad,
                    'valor_unitario': valor_unitario or 0.0,
                    'porcentaje_impuesto': 19.0
                }
                items.append(item)
            except Exception as e:
                print(f'Error procesando item: {e}')
                continue
        
        if not items:
            items = self._extraer_items_alternativo(texto)

        return items

    def _extraer_items_alternativo(self, texto):
        items = []
        lineas = texto.split('\n')
        
        patron_linea = re.compile(
           r'(\d{8})\s+(.+?)\s+NAR\s+(\d+(?:[.,]\d+)?)'
           r'.*?\$([0-9.,]+).*?\$([0-9.,]+)'
        )

        for linea in lineas:
            linea = linea.strip()
            if len(linea) < 20:
                continue
            match = patron_linea.search(linea)
            if match:
                try:
                    item = {
                        'codigo_producto': match.group(1),
                        'descripcion': match.group(2).strip(),
                        'cantidad': float(match.group(3).replace(',', '.')),
                        'valor_unitario': self._limpiar_numero(match.group(4)) or 0.0,
                        'porcentaje_impuesto': 19.0
                    }
                    items.append(item)
                except Exception as e:
                    print(f'Error en extracción alternativa de items: {e}')
                    continue
        return items