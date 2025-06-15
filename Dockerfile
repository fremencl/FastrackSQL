# Imagen base de Python 3.10
FROM python:3.10

# Crear directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo requirements al contenedor
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código del proyecto al contenedor
COPY . .

# Exponer el puerto que usa Streamlit por defecto
EXPOSE 8501

# Comando de inicio: ejecuta App.py
ENTRYPOINT ["streamlit", "run", "App.py", "--server.port=8501", "--server.address=0.0.0.0"]
