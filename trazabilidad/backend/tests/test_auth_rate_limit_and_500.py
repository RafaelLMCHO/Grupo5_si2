"""Tests de Rate Limiting en Login y Manejo Seguro de Errores 500 (Prompt 7).

Verifica:
1. Límite de 5 intentos fallidos en POST /auth/login por (email, IP) -> El 6to intento responde 429 Too Many Requests.
2. Login exitoso reinicia el contador de intentos fallidos.
3. El evento de bloqueo se audita y persiste en la tabla Bitácora (CU-005).
4. Errores 500 no controlados responden con mensaje genérico ("Error interno del servidor")
   sin fugar información interna sensible (sin "error_detail", "error_type" ni "trace").
"""
import pytest
from starlette.testclient import TestClient
from sqlalchemy import select, desc

from app.main import app
from app.packages.p1_seguridad.controllers.cu004_autenticacion.auth_controller import (
    login_rate_limiter,
    MAX_LOGIN_ATTEMPTS
)
from app.packages.p1_seguridad.models.cu005_bitacora.bitacora import Bitacora


@pytest.fixture(autouse=True)
def clean_rate_limiter():
    """Limpia el estado del rate limiter en memoria antes y después de cada test."""
    login_rate_limiter.reset()
    yield
    login_rate_limiter.reset()


def test_cinco_logins_fallidos_y_el_sexto_responde_429(client, setup_test_data):
    """5 intentos de login fallidos devuelven 401; el sexto devuelve 429 Too Many Requests."""
    email_target = "user1@test.com"
    tenant_target = "empresa-test-1"

    # 1. Ejecutar 5 intentos con credenciales incorrectas
    for i in range(MAX_LOGIN_ATTEMPTS):
        resp = client.post(
            "/api/v1/auth/login",
            json={
                "tenant_slug": tenant_target,
                "email": email_target,
                "password": f"WrongPassword_{i}!"
            }
        )
        assert resp.status_code == 401, f"El intento {i+1} debió devolver 401, devolvió {resp.status_code}"

    # 2. El 6to intento debe ser bloqueado con 429
    resp_bloqueado = client.post(
        "/api/v1/auth/login",
        json={
            "tenant_slug": tenant_target,
            "email": email_target,
            "password": "WrongPassword_6!"
        }
    )
    assert resp_bloqueado.status_code == 429
    assert "bloqueada" in resp_bloqueado.json()["detail"].lower()

    # 3. Incluso con la contraseña correcta debe permanecer bloqueado con 429
    resp_con_correcta = client.post(
        "/api/v1/auth/login",
        json={
            "tenant_slug": tenant_target,
            "email": email_target,
            "password": "MiClave@123"
        }
    )
    assert resp_con_correcta.status_code == 429
    assert "bloqueada" in resp_con_correcta.json()["detail"].lower()


def test_login_exitoso_reinicia_intentos_fallidos(client, setup_test_data):
    """Un login exitoso reinicia el contador de intentos fallidos antes de alcanzar el bloqueo."""
    email_target = "user1@test.com"
    tenant_target = "empresa-test-1"

    # Realizar 3 intentos fallidos
    for i in range(3):
        resp = client.post(
            "/api/v1/auth/login",
            json={
                "tenant_slug": tenant_target,
                "email": email_target,
                "password": f"WrongPassword_{i}!"
            }
        )
        assert resp.status_code == 401

    # El 4to intento es exitoso
    resp_ok = client.post(
        "/api/v1/auth/login",
        json={
            "tenant_slug": tenant_target,
            "email": email_target,
            "password": "MiClave@123"
        }
    )
    assert resp_ok.status_code == 200

    # Ahora puede volver a intentar 4 veces fallidas sin ser bloqueado
    for i in range(4):
        resp = client.post(
            "/api/v1/auth/login",
            json={
                "tenant_slug": tenant_target,
                "email": email_target,
                "password": f"AnotherWrong_{i}!"
            }
        )
        assert resp.status_code == 401


def test_bloqueo_registrado_en_bitacora(client, db_session, setup_test_data):
    """El bloqueo por fuerza bruta debe registrarse en la Bitácora (CU-005)."""
    email_target = "user1@test.com"
    tenant_target = "empresa-test-1"

    # 5 intentos fallidos para disparar el bloqueo
    for i in range(5):
        client.post(
            "/api/v1/auth/login",
            json={
                "tenant_slug": tenant_target,
                "email": email_target,
                "password": f"BadPassword_{i}!"
            }
        )

    # Verificar que exista la entrada en la tabla Bitacora
    stmt = (
        select(Bitacora)
        .where(
            Bitacora.accion == "BLOQUEO_LOGIN",
            Bitacora.entidad == "Autenticacion"
        )
        .order_by(desc(Bitacora.idbitacora))
    )
    registro = db_session.execute(stmt).scalars().first()
    assert registro is not None, "No se encontró el registro de BLOQUEO_LOGIN en Bitacora"
    assert registro.accion == "BLOQUEO_LOGIN"
    assert registro.entidad == "Autenticacion"


def test_error_500_forzado_no_contiene_error_detail():
    """Un error 500 no controlado no debe filtrar error_detail, error_type ni traces internos."""
    client_safe = TestClient(app, raise_server_exceptions=False)
    resp = client_safe.get("/api/v1/debug/force-500")

    assert resp.status_code == 500
    data = resp.json()
    assert "detail" in data
    assert data["detail"] == "Error interno del servidor"
    assert "error_detail" not in data
    assert "error_type" not in data
    assert "trace" not in data
