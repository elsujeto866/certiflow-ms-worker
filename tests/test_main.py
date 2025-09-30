"""
Tests básicos para la aplicación Certiflow.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test del endpoint raíz."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data
    assert data["status"] == "running"


def test_health_endpoint():
    """Test del endpoint de health check."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data
    assert "timestamp" in data


def test_templates_endpoint():
    """Test del endpoint de plantillas."""
    response = client.get("/api/v1/templates/")
    assert response.status_code == 200
    data = response.json()
    assert "templates" in data
    assert "count" in data


# Tests adicionales que puedes agregar:

# def test_upload_pdf_endpoint():
#     """Test de subida de PDF."""
#     # Necesitarías un archivo PDF de prueba
#     pass

# def test_extract_data_endpoint():
#     """Test de extracción de datos."""
#     # Necesitarías configurar OpenAI API key para pruebas
#     pass