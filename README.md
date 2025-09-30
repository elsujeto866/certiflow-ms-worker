# Certiflow API Worker 📄➡️🤖➡️📊

## 📝 Descripción

Este microservicio automatiza el proceso de extracción de datos y generación de reportes. Está diseñado para recibir un documento **PDF**, extraer su texto, usar un modelo de **OpenAI** para interpretar y estructurar la información en un objeto **JSON** y, finalmente, llenar una plantilla de **Excel** predefinida con esos datos.

---

## ✨ Características Principales

* **Recepción de PDFs:** Acepta archivos PDF a través de un endpoint de API simple.
* **Extracción de Texto:** Lee y extrae automáticamente el contenido textual del documento subido.
* **Análisis con IA:** Aprovecha el poder de OpenAI para entender el contexto y extraer puntos de datos específicos de texto no estructurado.
* **Salida JSON Estructurada:** Devuelve un objeto JSON limpio y predecible, facilitando el uso de los datos en otras aplicaciones.
* **Generación de Reportes en Excel:** Usa los datos del JSON estructurado para llenar automáticamente una hoja de cálculo de Excel predefinida, ahorrando horas de ingreso manual de datos.

---

## ⚙️ Flujo de Trabajo

El servicio sigue un flujo de trabajo simple y potente:

`Subida de PDF` ➡️ `Extracción de Texto` ➡️ `Envío a OpenAI` ➡️ `Recepción de JSON` ➡️ `Llenado de Plantilla Excel`

---

## 🚀 Cómo Empezar

Sigue estos pasos para tener una copia local del proyecto funcionando.

### Requisitos Previos

Asegúrate de tener Python 3.8+ instalado en tu sistema.

### Instalación

1.  **Clona el repositorio**
    ```sh
    git clone [https://github.com/tu-usuario/certiflow-api-worker.git](https://github.com/tu-usuario/certiflow-api-worker.git)
    ```

2.  **Navega al directorio del proyecto**
    ```sh
    cd certiflow-api-worker
    ```

3.  **Crea y activa un entorno virtual**
    * En macOS/Linux:
        ```sh
        python3 -m venv certiflow
        source certiflow/bin/activate
        ```
    * En Windows:
        ```sh
        python -m venv certiflow
        certiflow\Scripts\activate
        ```

4.  **Instala las dependencias**
    ```sh
    pip install -r requirements.txt
    ```

5.  **Configura tus credenciales**
    * Crea un archivo llamado `.env` en la raíz del proyecto.
    * Añade tu clave de API de OpenAI al archivo:
        ```
        OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        ```

---

## 🔧 Uso

1.  **Inicia el servidor**
    Ejecuta el siguiente comando en tu terminal. El flag `--reload` reiniciará el servidor automáticamente cada vez que hagas cambios en el código.
    ```sh
    uvicorn app.main:app --reload
    ```

2.  **Accede a la Documentación Interactiva**
    Abre tu navegador y ve a la siguiente URL para ver y probar la API en tiempo real:
    [**http://127.0.0.1:8000/docs**](http://127.0.0.1:8000/docs)

3.  **Envía una Petición**
    Puedes usar la interfaz de `/docs` para subir un archivo PDF al endpoint `/extract-data/` o usar una herramienta como `curl`:
    ```sh
    curl -X POST -F "file=@/ruta/a/tu/archivo.pdf" [http://127.0.0.1:8000/extract-data/](http://127.0.0.1:8000/extract-data/)
    ```