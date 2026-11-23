"""Tests para las 3 nuevas consultas de alto impacto del Asistente de Informes Dinámicos por Voz:
1. Rentabilidad y Margen Comercial (precio de venta vs costo promedio)
2. Control de Calidad, Garantías y Devoluciones (tasa de incidencias)
3. Seguridad Criptográfica, Blockchain y Alertas de Sospecha (inmutabilidad on-chain)
"""
from datetime import datetime
import pytest

from app.services.ai.voice_query_parser import parse_query


AHORA = datetime(2026, 11, 23, 12, 0)


def test_parser_entiende_rentabilidad_y_margen():
    parsed = parse_query(
        "Top 5 productos con mayor margen de ganancia en los últimos 6 meses",
        now=AHORA,
    )
    assert parsed.intent == "rentabilidad"
    assert parsed.limit == 5
    assert "ultimos 6 meses" in parsed.period_label
    assert "rentabilidad" in parsed.interpretation().lower()


def test_parser_entiende_garantias_y_devoluciones():
    parsed = parse_query(
        "¿Cuál es la tasa de devoluciones y garantías del último trimestre?",
        now=AHORA,
    )
    assert parsed.intent == "garantias"
    assert "3 meses" in parsed.period_label
    assert "garantías" in parsed.interpretation().lower()


def test_parser_entiende_blockchain_y_alertas():
    parsed = parse_query(
        "Unidades notarizadas en blockchain y alertas de sospecha",
        now=AHORA,
    )
    assert parsed.intent == "blockchain"
    assert "blockchain" in parsed.interpretation().lower()


def test_api_reporte_rentabilidad(client, auth_headers):
    response = client.post(
        "/api/v1/ai/voice-report",
        json={"query": "Top 5 productos con mayor margen de ganancia"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "rentabilidad"
    assert len(data["kpis"]) == 4
    assert "chart" in data
    assert any("Margen" in h for h in data["table_headers"])
    assert data["pdf_download_url"].startswith("/api/v1/ai/reports/")
    assert data["excel_download_url"].startswith("/api/v1/ai/reports/")
    assert "voice_summary" in data
    assert "executive_summary" in data


def test_api_reporte_garantias_calidad(client, auth_headers):
    response = client.post(
        "/api/v1/ai/voice-report",
        json={"query": "Tasa de devoluciones y garantías de los últimos 6 meses"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "garantias"
    assert len(data["kpis"]) == 4
    assert any("Garantía" in h or "Devoluciones" in h for h in data["table_headers"])
    assert "voice_summary" in data
    assert "executive_summary" in data


def test_api_reporte_blockchain_seguridad(client, auth_headers):
    response = client.post(
        "/api/v1/ai/voice-report",
        json={"query": "Unidades notarizadas en blockchain y alertas de sospecha"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "blockchain"
    assert len(data["kpis"]) == 4
    assert any("Hash" in h or "Red" in h for h in data["table_headers"])
    assert "voice_summary" in data
    assert "executive_summary" in data


def test_api_reporte_pdf_export_con_graficos(client, auth_headers):
    # Generar reporte
    rep = client.post(
        "/api/v1/ai/voice-report",
        json={"query": "Top 5 productos con mayor margen de ganancia"},
        headers=auth_headers,
    )
    assert rep.status_code == 200
    pdf_url = rep.json()["pdf_download_url"]

    # Descargar PDF exportado con gráfico embebido
    pdf_resp = client.get(pdf_url, headers=auth_headers)
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert len(pdf_resp.content) > 1000
    assert b"%PDF" in pdf_resp.content[:10]
