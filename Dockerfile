# 1. Imagen base: Empezamos con una versión ligera de Python.
FROM python:3.11-slim

# 2. Directorio de trabajo: Creamos una carpeta dentro del contenedor para nuestro código.
WORKDIR /code

# 3. Copiar e instalar dependencias: Este es un paso optimizado.
# Copiamos solo el archivo de requisitos primero...
COPY ./requirements.txt /code/requirements.txt
# ...y luego instalamos las librerías.
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 4. Copiar el código de la aplicación: Ahora copiamos el resto de nuestra app.
COPY ./app /code/app

# 5. Exponer el puerto: Le decimos a Docker que el contenedor escuchará en el puerto 8000.
EXPOSE 8000

# 6. Comando de ejecución: Esto es lo que se ejecuta cuando el contenedor arranca.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]