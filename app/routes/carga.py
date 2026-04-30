import os
from flask import Blueprint,render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Factura, ItemFactura, ConfiguracionEmpresa, Auditoria
from app.services.extractor_ocr import ExtractorOCR
from datetime import datetime

carga = Blueprint('carga', __name__)

EXTENSIONES_PERMITIDAS = {'pdf'}

def archivo_permitido(nombre_archivo):
    return '.' in nombre_archivo and nombre_archivo.rsplit('.', 1)[1].lower() in EXTENSIONES_PERMITIDAS

def convertir_fecha(texto_fecha):
    if not texto_fecha:
        return None
    formatos = [
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%Y-%m-%d',
        '%d/%m/%y',
    ]
    for formato in formatos:
        try:
            return datetime.strptime(texto_fecha.strip(), formato).date()
        except ValueError:
            continue
    return None

@carga.route('/carga', methods=['GET', 'POST'])
@login_required
def subir_factura():
    if request.method == 'POST':

        if 'archivo' not in request.files:
            flash('No se seleccionó ningún archivo', 'danger')
            return redirect(url_for('carga.subir_factura'))

        archivo = request.files['archivo']

        if archivo.filename == '':
            flash('No se seleccionó ningún archivo', 'danger')
            return redirect(url_for('carga.subir_factura'))

        if not archivo_permitido(archivo.filename):
            flash('Solo se permiten archivos pdf', 'danger')
            return redirect(url_for('carga.subir_factura'))

        config = ConfiguracionEmpresa.query.filter_by(activo=True).first()
        if not config:
            flash('Primero debes configurar los datos de la empresa.', 'warning')
            return redirect(url_for('configuracion.ver_configuracion'))

        nombre_seguro = secure_filename(archivo.filename)
        ruta_guardado = os.path.join(current_app.config['UPLOAD_FOLDER'], nombre_seguro)

        try:
            archivo.save(ruta_guardado)
        except Exception as e:
            flash(f'Error al guardar el archivo: {str(e)}', 'danger')
            return redirect(url_for('carga.subir_factura'))

        try:       
            extractor = ExtractorOCR()
            resultado = extractor.procesar_pdf(ruta_guardado)
            print(f'Resultado del extractor: {resultado}')
            cabecera = resultado['cabecera']
            items = resultado['items']

            nueva_factura = Factura(
                id_usuario_carga=current_user.id_usuario,
                id_config=config.id_config,
                numero_factura=cabecera.get('numero_factura') or 'POR_REVISAR',
                nit_proveedor=cabecera.get('nit_proveedor') or 'POR_REVISAR',
                proveedor=cabecera.get('proveedor') or '',
                fecha_emision=convertir_fecha(cabecera.get('fecha_emision')),
                subtotal=0.0,
                total_impuestos=0.0,
                total_pagar=0.0,
                estado='CARGADA',
                ruta_archivo=ruta_guardado
            )
            db.session.add(nueva_factura)
            db.session.flush()

            for item_data in items:
                cantidad = float(item_data.get('cantidad') or 0)
                valor_unitario = float(item_data.get('valor_unitario') or 0)
                porcentaje_impuesto = float(
                    item_data.get('porcentaje_impuesto') or 0)

                valor_impuesto = round(
                    (cantidad * valor_unitario) *
                    (porcentaje_impuesto / 100), 2)
                valor_total = round(
                    (cantidad * valor_unitario) + valor_impuesto, 2)

                nuevo_item = ItemFactura(
                    id_factura=nueva_factura.id_factura,
                    descripcion=item_data.get('descripcion', ''),
                    cantidad=cantidad,
                    valor_unitario=valor_unitario,
                    porcentaje_impuesto=porcentaje_impuesto,
                    valor_impuesto=valor_impuesto,
                    valor_total=valor_total,
                    codigo_producto=item_data.get('codigo_producto', '')
                )
                db.session.add(nuevo_item)
                
            nueva_factura.subtotal = round(sum(
                float(i.get('cantidad') or 0) *
                float(i.get('valor_unitario') or 0)
                for i in items), 2)
            nueva_factura.total_impuestos = round(sum(
                (float(i.get('cantidad') or 0) *
                float(i.get('valor_unitario') or 0)) *
                (float(i.get('porcentaje_impuesto') or 0) / 100)
                for i in items), 2)
            nueva_factura.total_pagar = round(
                nueva_factura.subtotal +
                nueva_factura.total_impuestos, 2)

            auditoria = Auditoria(
                id_usuario=current_user.id_usuario,
                accion='CARGA',
                tabla_afectada='factura',
                id_referencia=nueva_factura.id_factura,
                detalles=f'factura cargada desde archivo: {nombre_seguro}'
            )
            db.session.add(auditoria)
            db.session.commit()
            
            flash(f'Factura procesada exitosamente. Revisa los datos extraídos.', 'success')
            return redirect(url_for('carga.subir_factura'))

        except Exception as e:
            db.session.rollback()
            if os.path.exists(ruta_guardado):
                os.remove(ruta_guardado)
            print(f'Error procesando factura: {str(e)}')
            flash('Ocurrio un error al procesar la factura.' ' Por favor intenta de nuevo.', 'danger' )
            return redirect(url_for('carga.subir_factura'))              

    return render_template('carga.html')