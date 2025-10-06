# 1. Imagen base: Empezamos con una versión ligera de Python.
FROM python:3.11-slim

# 2. Instalar dependencias del sistema (si necesitas alguna)
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# 3. Crear usuario no-root para seguridad
RUN adduser --disabled-password --gecos '' appuser

# 4. Directorio de trabajo: Creamos una carpeta dentro del contenedor para nuestro código.
WORKDIR /code

# 5. Copiar e instalar dependencias: Este es un paso optimizado.
# Copiamos solo el archivo de requisitos primero...
COPY ./requirements.txt /code/requirements.txt
# ...y luego instalamos las librerías.
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 6. Copiar el código de la aplicación: Ahora copiamos el resto de nuestra app.
COPY ./app /code/app

# 7. Crear directorios necesarios
RUN mkdir -p /code/uploads /code/output /code/templates /code/logs

# 8. Cambiar permisos al usuario no-root
RUN chown -R appuser:appuser /code
USER appuser

# 9. Exponer el puerto: Le decimos a Docker que el contenedor escuchará en el puerto 8000.
EXPOSE 8000

# 10. Comando de ejecución: Esto es lo que se ejecuta cuando el contenedor arranca.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]