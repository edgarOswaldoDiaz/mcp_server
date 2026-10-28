FROM python:3.12-slim

# Evita archivos .pyc y permite ver logs inmediatamente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias primero para aprovechar la caché de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto (src, etc.)
COPY . .

# El nodo A2A del Equipo B escucha en este puerto interno
EXPOSE 8001

# Ejecutar FastAPI para el nodo A2A
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
