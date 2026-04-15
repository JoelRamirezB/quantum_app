from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Factura, ItemFactura, Auditoria

validacion = Blueprint('validacion', __name__)

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

@validacion.route('/validacion')
@login_required
def lista_validacion():
    facturas_pendientes = Factura.query.filter(Factura.estado.in_(['CARGADA', 'ERROR'])).order_by(Factura.fecha_carga.desc()).all()
    return render_template('validacion_lista.html', facturas=facturas_pendientes)

@validacion.route('/validacion/<int:id_factura>', methods=['GET', 'POST'])
@login_required
def ver_factura(id_factura):
    factura = Factura.query.get_or_404(id_factura)

    if factura.estado == 'EXPORTADA':
        flash('Esta factura ya fue exportada y no puede ser modificada', 'warning')
        return redirect(url_for('validacion.lista_validacion'))

    if request.method == 'POST':
        accion = request.form.get('accion')

        if accion == 'guardar':
            factura.numero_factura = (request.form.get('numero_factura') or 'POR_REVISAR')
            factura.nit_proveedor = (request.form.get('nit_proveedor') or 'POR_REVISAR')
            factura.proveedor = (request.form.get('proveedor') or '')
            factura.tipo_factura = (request.form.get('tipo_factura') or 'COMPRA')
            factura.metodo_pago = (request.form.get('metodo_pago') or 'Credito')

            fecha_texto = request.form.get('fecha_emision')
            factura.fecha_emision = convertir_fecha(fecha_texto)

            items_ids = request.form.getlist('item_id')
            for item_id in items_ids:
                item = ItemFactura.query.get(int(item_id))
                if item and item.id_factura == factura.id_factura:
                    item.descripcion = request.form.get(f'descripcion_{item_id}', '')
                    item.cantidad = float(request.form.get(f'cantidad_{item_id}', 1) or 1)
                    item.valor_unitario = float(request.form.get(f'valor_unitario_{item_id}', 0) or 0 )
                    item.porcentaje_impuesto = float(request.form.get(f'porcentaje_impuesto_{item_id}', 19) or 19)
            db.session.commit()

            auditoria = Auditoria(
                id_usuario=current_user.id_usuario, 
                accion='EDICION', 
                tabla_afectada='factura', 
                id_referencia=factura.id_factura, 
                detalles=f'Factura {factura.numero_factura} ' 'editada manualmente'
            )
            db.session.add(auditoria)
            db.session.commit()

            flash('Cambios guaradados exitosamente', 'success')
            return redirect(url_for('validacion.ver_factura', id_factura=id_factura))

        elif accion == 'validar':
            factura.estado = 'VALIDADA'
            factura.id_usuario_validador = (current_user.id_usuario)
            factura.fecha_validacion = datetime.utcnow()

            db.session.commit()

            auditoria = Auditoria(
                id_usuario=current_user.id_usuario,
                accion='VALIDACION',
                tabla_afectada='factura',
                id_referencia=factura.id_factura,
                detalles=f'Factura {factura.numero_factura}' 'validada'
            )
            db.session.add(auditoria)
            db.session.commit()

            flash('Cambios validada exitosamente', 'success')
            return redirect(url_for('validacion.lista_validacion'))

        elif accion == 'rechazar':
            factura.estado = 'ERROR'
            db.session.commit()

            auditoria = Auditoria(
                id_usuario=current_user.id_usuario,
                accion='RECHAZO',
                tabla_afectada='factura',
                id_referencia=factura.id_factura,
                detalles=f'Factura {factura.numero_factura}' 'rechazada'
            )
            db.session.add(auditoria)
            db.session.commit()

            flash('Factura rechazada', 'warning')
            return redirect(url_for('validacion.lista_validacion'))

    return render_template('validacion_detalle.html', factura=factura)

