# Certiflow API Worker - Estructura del Proyecto

Este documento describe la estructura del proyecto y cómo está organizado.

## 📁 Estructura de Directorios

```
certiflow-api-worker/
├── app/                          # Código principal de la aplicación
│   ├── __init__.py
│   ├── main.py                   # Aplicación FastAPI principal
│   ├── api/                      # Endpoints y rutas
│   │   ├── __init__.py
│   │   └── routes.py             # Rutas de la API
│   ├── core/                     # Configuración y utilidades centrales
│   │   ├── __init__.py
│   │   ├── config.py             # Configuración y settings
│   │   └── logging.py            # Configuración de logging
│   ├── models/                   # Modelos de datos y esquemas
│   │   ├── __init__.py
│   │   ├── schemas.py            # Esquemas Pydantic
│   │   └── exceptions.py         # Excepciones personalizadas
│   ├── services/                 # Lógica de negocio y servicios
│   │   ├── __init__.py
│   │   ├── pdf_service.py        # Procesamiento de PDFs
│   │   ├── openai_service.py     # Integración con OpenAI
│   │   └── excel_service.py      # Generación de Excel
│   └── utils/                    # Utilidades y helpers
│       ├── __init__.py
│       ├── file_utils.py         # Utilidades de archivos
│       └── validators.py         # Validadores y helpers
├── templates/                    # Plantillas Excel (crear aquí tus plantillas)
├── uploads/                      # Archivos subidos temporalmente
├── output/                       # Archivos Excel generados
├── tests/                        # Tests unitarios y de integración
├── logs/                         # Archivos de log
├── main.py                       # Punto de entrada (compatibilidad)
├── requirements.txt              # Dependencias Python
├── .env.example                  # Ejemplo de configuración
├── .gitignore                    # Archivos ignorados por Git
└── README.md                     # Documentación principal
```

## 🔧 Componentes Principales

### 1. **app/main.py**
- Aplicación FastAPI principal
- Configuración de middleware
- Manejo de excepciones globales
- Endpoints de health check

### 2. **app/api/routes.py**
- Endpoints para subir PDFs
- Endpoint principal de extracción de datos
- Endpoints para descargar Excel generados
- Endpoint para listar plantillas

### 3. **app/services/**
- **pdf_service.py**: Extrae texto de archivos PDF usando PyPDF2
- **openai_service.py**: Integra con OpenAI para estructurar datos
- **excel_service.py**: Genera archivos Excel con los datos extraídos

### 4. **app/models/**
- **schemas.py**: Modelos Pydantic para requests/responses
- **exceptions.py**: Excepciones personalizadas de la aplicación

### 5. **app/core/**
- **config.py**: Configuración usando variables de entorno
- **logging.py**: Sistema de logging estructurado

## 🚀 Cómo Usar

### 1. Configuración
1. Copia `.env.example` a `.env`
2. Configura tu `OPENAI_API_KEY`

### 2. Instalación
```bash
pip install -r requirements.txt
```

### 3. Ejecutar
```bash
# Opción 1: Usando el archivo principal
python main.py

# Opción 2: Usando uvicorn directamente
uvicorn app.main:app --reload

# Opción 3: Como se menciona en el README
uvicorn app.main:app --reload
```

### 4. Acceder a la documentación
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## 📋 Endpoints Disponibles

- `GET /` - Información básica del servicio
- `GET /health` - Health check
- `POST /api/v1/upload-pdf/` - Subir archivo PDF
- `POST /api/v1/extract-data/` - Procesar PDF y extraer datos
- `GET /api/v1/download-excel/{filename}` - Descargar Excel generado
- `GET /api/v1/templates/` - Listar plantillas disponibles

## 🎯 Flujo de Trabajo

1. **Cliente sube PDF** → `/api/v1/extract-data/`
2. **Sistema valida archivo** → Verifica tamaño, tipo, etc.
3. **Extrae texto del PDF** → Usando PyPDF2
4. **Procesa con OpenAI** → Estructura los datos en JSON
5. **Genera Excel** → Usando plantilla o formato por defecto
6. **Retorna resultados** → JSON con datos + ruta del Excel

## 🛠️ Personalización

### Agregar Nuevas Plantillas Excel
1. Coloca tu archivo `.xlsx` en la carpeta `templates/`
2. Usa el parámetro `template_name` en el endpoint

### Modificar Campos Extraídos
1. Edita `app/models/schemas.py` para cambiar `ExtractedData`
2. Ajusta el prompt en `app/services/openai_service.py`

### Agregar Nuevos Endpoints
1. Añade rutas en `app/api/routes.py`
2. Registra el router en `app/main.py`

## 🔒 Seguridad

- Variables de entorno para configuración sensible
- Validación de archivos subidos
- Límites de tamaño de archivo
- Logging de errores y actividades

## 📝 Logs

Los logs se guardan en:
- Consola (desarrollo)
- Archivo `logs/app.log` (producción)

Niveles de log configurables mediante variables de entorno.