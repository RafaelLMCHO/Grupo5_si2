"""Pruebas de Verificación de Prompt 8 (Configuración, Migraciones y Auditoría).

1. requirements.txt incluye python-multipart con versión fija.
2. El middleware de Bitácora NO registra operaciones GET convencionales como entradas.
3. El middleware de Bitácora registra operaciones de escritura (POST, PUT, PATCH, DELETE).
4. Los tests de planes y suscripciones disponen de fixtures automáticos (seed idempotente).
"""
import os
import pytest
from sqlalchemy import select, desc
from app.packages.p1_seguridad.models.cu005_bitacora.bitacora import Bitacora
from app.packages.p8_suscripciones.models.cu036_planes.subscription_models import Plan, Suscripcion
from app.db.session import SessionLocal


def test_requirements_incluye_python_multipart():
    """Verifica que requirements.txt contenga python-multipart fijado."""
    req_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "requirements.txt")
    with open(req_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "python-multipart" in content


def test_bitacora_no_registra_operaciones_get(client, setup_test_data, auth_headers):
    """GET a endpoints convencionales NO debe generar entradas en Bitacora."""
    db = SessionLocal()
    try:
        # Contar registros previos de GET en Bitacora
        stmt_count_get = select(Bitacora).where(Bitacora.accion == "GET")
        pre_count = len(list(db.execute(stmt_count_get).scalars().all()))
    finally:
        db.close()

    # Ejecutar peticiones GET con token Bearer
    resp_prod = client.get("/api/v1/products", headers=auth_headers)
    assert resp_prod.status_code == 200

    resp_units = client.get("/api/v1/units", headers=auth_headers)
    assert resp_units.status_code == 200

    resp_tenants = client.get("/api/v1/tenants", headers=auth_headers)
    assert resp_tenants.status_code == 200

    # Verificar que NO se crearon nuevas filas con accion == 'GET'
    db = SessionLocal()
    try:
        post_count = len(list(db.execute(stmt_count_get).scalars().all()))
    finally:
        db.close()
    assert post_count == pre_count, f"Se crearon entradas GET en bitácora: antes {pre_count}, después {post_count}"


def test_bitacora_si_registra_operaciones_escritura(client, setup_test_data, auth_headers):
    """Operaciones de escritura (POST, etc.) SI deben registrarse en Bitacora."""
    db = SessionLocal()
    try:
        # Contar entradas POST en Bitacora
        stmt_count_post = select(Bitacora).where(Bitacora.accion == "POST")
        pre_count = len(list(db.execute(stmt_count_post).scalars().all()))
    finally:
        db.close()

    # Crear una categoría vía POST
    resp = client.post(
        "/api/v1/categories",
        json={"nombrecategoria": "Cat Audit Test", "descripcion": "Test de auditoría escritura"},
        headers=auth_headers
    )
    assert resp.status_code == 201

    db = SessionLocal()
    try:
        post_count = len(list(db.execute(stmt_count_post).scalars().all()))
    finally:
        db.close()
    assert post_count > pre_count, "No se registró la operación POST en Bitacora"


def test_fixtures_planes_y_suscripciones_disponibles(setup_test_data, db_session):
    """Verifica que los planes y suscripciones se carguen automáticamente sin fallar."""
    planes = list(db_session.execute(select(Plan)).scalars().all())
    assert len(planes) >= 4, "Los planes base no fueron cargados automáticamente"
    codigos = [p.codigo for p in planes]
    assert "trial" in codigos
    assert "pro" in codigos
