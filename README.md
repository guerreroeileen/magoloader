# MagoLoader

Aplicación de escritorio para descargar videos de TikTok por perfil.

## Requisitos

- Python 3.10+
- Conexión a internet

## Instalación

```bash
pip install -r requirements.txt
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

## Tecnologías

- **Interfaz:** CustomTkinter (tema oscuro, acentos rojos estilo TikTok).
- **Descargas:** yt-dlp (sin APIs oficiales ni API keys).
- **Concurrencia:** Tareas de red en hilos separados para no bloquear la UI.
