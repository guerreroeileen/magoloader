# MagoLoader

Aplicación de escritorio para descargar videos de TikTok por perfil.

## Requisitos

- Python 3.10+
- `yt-dlp[curl-cffi]>=2026.8.19` (con soporte de suplantación de navegador `curl-cffi` para evitar bloqueos SSL/TLS con TikTok)
- Conexión a internet

## Instalación

```bash
pip install -r requirements.txt
```

Si necesitas actualizar `yt-dlp` a la última versión disponible desde la terminal:

```bash
pip install -U "yt-dlp[curl-cffi]"
```

## Uso

```bash
python main.py
```

1. Escribe un **@usuario** de TikTok en el campo del header y pulsa **Analizar**.
2. Revisa el perfil en la barra izquierda y la lista de videos en el centro.
3. Elige la carpeta de guardado con **Examinar...** (por defecto: `Downloads/MagoLoader`).
4. Marca o desmarca videos con los checkboxes y usa **Seleccionar todos** si quieres.
5. Pulsa **Descargar seleccionados** y sigue el progreso en la barra inferior.

Los archivos se guardan con el formato `[Fecha]_[Título].mp4`.

## Crear una nueva versión (Release)

Sigue estos pasos para generar el ejecutable standalone y lanzar una nueva versión de MagoLoader:

### 1. Actualizar la versión en el código
Edita el archivo `magoloader/version.py` y define el número de versión (ejemplo `1.2.0`):

```python
__version__ = "1.2.0"
```

### 2. Limpiar y construir el ejecutable
Ejecuta el script de construcción automatizado:

```bash
python build.py
```

Este script:
- Limpia las carpetas anteriores `build/` y `dist/`.
- Ejecuta PyInstaller con las opciones `--noconsole`, `--onefile`, `--icon=magoloader.ico` e incluye las dependencias necesarias (`customtkinter`, `curl_cffi`).
- Genera el archivo ejecutable standalone en `dist/MagoLoader.exe`.

### 3. Probar el binario generado
Ejecuta y verifica la aplicación compilada:

```bash
dist/MagoLoader.exe
```

### 4. Crear Tag en Git y Publicar la versión
Crea la etiqueta de versión en Git y súbela al repositorio:

```bash
git add .
git commit -m "chore: release v1.2.0"
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin main --tags
```

En **GitHub**:
1. Ve a la sección **Releases** > **Draft a new release**.
2. Selecciona la etiqueta creada (`v1.2.0`).
3. Escribe el título y las notas de la versión (Changelog).
4. Adjunta el ejecutable `dist/MagoLoader.exe` como asset binario de la versión.
5. Publica la release.

## Tecnologías

- **Interfaz:** CustomTkinter (tema oscuro, acentos rojos estilo TikTok).
- **Descargas:** yt-dlp con `curl-cffi` (versión `2026.8.19`+).
- **Concurrencia:** Tareas de red en hilos separados para no bloquear la UI.

