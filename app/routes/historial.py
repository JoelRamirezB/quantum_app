from flask import Blueprint, render_template, request
from flask_login import login_required
from app.models import Factura
from datetime import datetime

historial = Blueprint('historial', __name__)

@historial.route('/historial')
@login_required
def ver_historial():
    query = Factura.query

    estado_filtro = request.args.get('estado', '')
    if estado_filtro:
        query = query.filter_by(estado=estado_filtro)

    prveedor_filtro = request.args.get('proveedor', '')
    if prveedor_filtro:
        query = query.filter(Factura.proveedor.ilike(f'%{prveedor_filtro}'))

    fecha_desde = request.args.get('fecha_desde', '')
    if fecha_desde:
        try:
            fecha = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            query = query.filter(Factura.fecha_carga >= fecha)
        except ValueError:
            pass

    fecha_hasta = request.args.get('fecha_hasta', '')
    if fecha_hasta:
        try:
            fecha = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            query = query.filter(Factura.fecha_carga <= fecha)
        except ValueError:
            pass

    facturas = query.order_by(Factura.fecha_carga.desc()).all()

    return render_template(
        'historial.html',
        facturas=facturas,
        estado_filtro=estado_filtro,
        prveedor_filtro=prveedor_filtro,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta
    )
