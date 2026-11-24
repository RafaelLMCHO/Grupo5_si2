"""Tests para el Asistente de Informes Dinámicos por Voz - Comparación Multi-Empresa (SuperAdmin):
1. Parser reconoce intenciones de comparación y benchmark entre empresas.
2. SuperAdministrador genera reporte comparativo con KPIs agregados, ranking y gráfico de barras.
3. Usuarios sin rol SuperAdministrador reciben 403 Forbidden al intentar generar reporte comparativo.
4. Exportación de reporte comparativo (PDF / Excel) valida privilegio SuperAdministrador.
"""
from datetime import datetime
import pytest
from sqlalchemy import select

from app.services.ai.voice_query_parser import parse_query
from app.models.cu002_usuarios.user import User
from app.models.cu002_usuarios.usuario_tenant import UsuarioTenant
from app.models.cu003_roles_permisos.role import Role
from app.models.cu003_roles_permisos.usuario_tenant_rol import UsuarioTenantRol


AHORA = datetime(2026, 11, 24, 12, 0)


def test_parser_reconoce_comparacion_tenants():
    queries = [
        "comparativa de ventas entre todas las empresas",
        "ranking de empresas por facturación",
        "comparar empresas en stock",
        "benchmark de empresas",
        "ventas por empresa",
        "stock por empresa",
    ]
    for q in queries:
        parsed = parse_query(q, now=AHORA)
        assert parsed.intent == "comparacion_tenants", f"Fallo al parsear '{q}'"
        assert "Benchmark Comparativo Multi-Empresa" in parsed.interpretation()


def test_api_reporte_comparacion_superadmin(client, auth_headers):
    response = client.post(
        "/api/v1/ai/voice-report",
        json={"query": "Comparativa de ventas entre todas las empresas"},
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["category"] == "comparacion_tenants"
    assert len(data["kpis"]) == 4
    assert any("Líder" in k["label"] for k in data["kpis"])
    assert "chart" in data
    assert data["chart"]["chart_type"] == "bar"
    assert "Empresa" in data["table_headers"]
    assert data["pdf_download_url"].startswith("/api/v1/ai/reports/")
    assert data["excel_download_url"].startswith("/api/v1/ai/reports/")
    assert "voice_summary" in data
    assert "executive_summary" in data
    assert "suggested_followups" in data
    assert len(data["suggested_followups"]) >= 3


def test_api_reporte_comparacion_no_superadmin_403(client, db_session, setup_test_data):
    # user2 en tenant2 con rol GestorVentasPostventa (no SuperAdmin)
    u2 = setup_test_data["user2"]
    t2 = setup_test_data["tenant2"]

    ut2 = db_session.execute(
        select(UsuarioTenant).where(
            UsuarioTenant.idusuario == u2.idusuario,
            UsuarioTenant.idtenant == t2.idtenant,
        )
    ).scalar_one()

    rol_gestor = db_session.execute(
        select(Role).where(Role.nombrerol == "GestorVentasPostventa")
    ).scalar_one_or_none()
    if not rol_gestor:
        rol_gestor = Role(nombrerol="GestorVentasPostventa", descripcion="Gestor Ventas")
        db_session.add(rol_gestor)
        db_session.flush()

    db_session.add(UsuarioTenantRol(idusuariotenant=ut2.idusuariotenant, idrol=rol_gestor.idrol))
    db_session.commit()

    # Login como user2
    resp_login = client.post(
        "/api/v1/auth/login",
        json={
            "tenant_slug": "empresa-test-2",
            "email": "user2@test.com",
            "password": "OtroPassword@456",
        },
    )
    assert resp_login.status_code == 200, resp_login.text
    user2_headers = {"Authorization": f"Bearer {resp_login.json()['access_token']}"}

    # Intentar generar reporte cross-tenant
    resp_report = client.post(
        "/api/v1/ai/voice-report",
        json={"query": "Comparar todas las empresas del sistema"},
        headers=user2_headers,
    )
    assert resp_report.status_code == 403
    assert "SuperAdministrador" in resp_report.json()["detail"]


def test_api_export_comparacion_valida_superadmin(client, auth_headers, db_session, setup_test_data):
    # 1. SuperAdmin genera reporte comparativo
    rep = client.post(
        "/api/v1/ai/voice-report",
        json={"query": "Ranking de empresas por facturación"},
        headers=auth_headers,
    )
    assert rep.status_code == 200
    pdf_url = rep.json()["pdf_download_url"]

    # 2. SuperAdmin puede descargar el documento
    resp_pdf_super = client.get(pdf_url, headers=auth_headers)
    assert resp_pdf_super.status_code == 200
    assert resp_pdf_super.headers["content-type"] == "application/pdf"

    # 3. Usuario regular no puede descargar un reporte cross-tenant
    u2 = setup_test_data["user2"]
    t2 = setup_test_data["tenant2"]
    ut2 = db_session.execute(
        select(UsuarioTenant).where(
            UsuarioTenant.idusuario == u2.idusuario,
            UsuarioTenant.idtenant == t2.idtenant,
        )
    ).scalar_one()
    rol_gestor = db_session.execute(
        select(Role).where(Role.nombrerol == "GestorVentasPostventa")
    ).scalar_one_or_none()
    if not rol_gestor:
        rol_gestor = Role(nombrerol="GestorVentasPostventa", descripcion="Gestor Ventas")
        db_session.add(rol_gestor)
        db_session.flush()
    db_session.add(UsuarioTenantRol(idusuariotenant=ut2.idusuariotenant, idrol=rol_gestor.idrol))
    db_session.commit()

    resp_login = client.post(
        "/api/v1/auth/login",
        json={
            "tenant_slug": "empresa-test-2",
            "email": "user2@test.com",
            "password": "OtroPassword@456",
        },
    )
    assert resp_login.status_code == 200
    user2_headers = {"Authorization": f"Bearer {resp_login.json()['access_token']}"}

    resp_pdf_forbidden = client.get(pdf_url, headers=user2_headers)
    assert resp_pdf_forbidden.status_code == 403
