import pdfplumber
import pytesseract
from PIL import Image
import re 
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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
        'subtotal': None,
        'total_impuestos': None,
        'total_pagar': None,
    }
    if not texto:
        return cabecera

    patrones_factura = [
        r'(?:Factura|FACTURA|FV|FE|No\.?|Número|NUMERO)[:\s#]*([A-Z0-9\-]+)',
        r'(?:Factura electrónica|FACTURA ELECTRÓNICA)[:\s#]*([A-Z0-9\-]+)'
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

    patrones_fecha = [
        r'(?:Fecha|FECHA)[:\s]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
        r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})'
    ]
    for patron in patrones_fecha:
        match = re.search(patron, texto)
        if match:
            cabecera['nit_emision'] = match.group(1).strip()
            break

    patrones_total = [
        r'(?:Total|TOTAL|Total a pagar|TOTAL A PAGAR)[:\s\$]*([0-9]{1,3}(?:[.,][0,9]{3})*(?:[.,][0-9]{2})?)',
        r'(?:Valor total|VALOR TOTAL)[:\s\$]*([0-9]{1,3}(?:[.,][0,9]{3})*(?:[.,][0-9]{2})?)'
    ]
    for patron in patrones_total:
        match = re.search(patron, texto)
        if match:
            valor_texto = match.group(1).replace('.', '').replace(',', '.')
            try:
                cabecera['total_pagar'] = float(valor_texto)
            except:
                pass
            break

def _extraer_items(self, texto):
    items = []
    if not texto:
        return items

    lineas = texto.split('\n')
    patron_item = r'(.+?)\s+(\d+(?:[.,]\d+)?)\s+\$?\s*([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{2})?)\s+\$?\s*([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{2})?)'
    for linea in lineas:
        linea = linea.strip()
        if len(linea) < 10:
            continue
        match = re.search(patron_item, linea)
        if match:
            try:
                cantidad_texto = match.group(2).replace(',', '.')
                valor_unit_texto = match.group(3).replace('.', '').replace(',', '.')
                valor_total_texto = match.group(4).replace('.', '').replace(',', '.')
                item = {
                    'descripcion': match.group(1).strip(),
                    'cantidad': float(cantidad_texto),
                    'valor_unitario': float(valor_unit_texto),
                    'valor_total': float(valor_total_texto),
                    'porcentaje_impuesto': 0.0 ,
                    'codigo_producto': '',
                }
                items.append(item)
            except:
                continue