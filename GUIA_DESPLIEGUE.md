# Guía de Despliegue y Docker

Este documento explica cómo usar los archivos de configuración Docker que se han añadido al proyecto.

## Ubicación de los archivos
Todos los archivos se han guardado en la carpeta raíz de tu proyecto (`c:\Sistemas ABBAMAT\ControlDeVacaciones\`):
- `Dockerfile`: Instrucciones para construir la imagen de tu aplicación.
- `docker-compose.yml`: Configuración para probar la app localmente con base de datos.
- `requirements.txt`: Lista de librerías necesarias.

## 1. Usar Docker Localmente (Pruebas)
Si decides instalar Docker Desktop en el futuro:

1.  Abre una terminal en la carpeta del proyecto.
2.  Ejecuta: `docker compose up --build`
3.  Docker descargará MySQL, configurará la base de datos y levantará tu aplicación.
4.  Podrás verla en `http://localhost:8000`.

## 2. Despliegue en la Nube (Web)

### Opción A: PythonAnywhere (Sin Docker)
1.  Sube tu código a GitHub.
2.  En PythonAnywhere, clona tu repositorio.
3.  Usa el archivo `requirements.txt` para instalar dependencias:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configura el archivo WSGI y la base de datos según sus guías.

### Opción B: Render / Railway (Con Docker)
1.  Sube tu código a GitHub (debe incluir el `Dockerfile`).
2.  Crea una cuenta en Render.com o Railway.app.
3.  Conecta tu cuenta de GitHub y selecciona este repositorio.
4.  El servicio detectará automáticamente el `Dockerfile` y construirá tu aplicación.
5.  **Nota**: Necesitarás configurar una base de datos MySQL en el mismo servicio (Railway ofrece una fácil) y poner las credenciales en las "Variables de Entorno" del servicio.
