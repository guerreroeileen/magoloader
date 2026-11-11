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

## Desarrollo de nuevas funcionalidades (OpenSpec)

El proyecto sigue un flujo **spec-driven** con [OpenSpec](https://github.com/Fission-AI/OpenSpec): antes de escribir código, cada funcionalidad o cambio de comportamiento se describe en una *change* (propuesta, diseño, specs y tareas) que luego se implementa y se archiva.

### Requisitos para desarrollar

- Python 3.10+ y las dependencias: `pip install -r requirements.txt`
- Node.js 20+ y la CLI de OpenSpec:

  ```bash
  npm install -g @fission-ai/openspec@latest
  ```

- Un asistente de IA configurado para el proyecto: **Claude Code** (lee `CLAUDE.md` y `.claude/`) o **Antigravity** (lee `.agents/`).

### Estructura

| Ruta | Contenido |
|------|-----------|
| `openspec/config.yaml` | Contexto del proyecto y reglas que la IA aplica en cada artefacto (proposal, design, tasks) y operación (apply, archive). |
| `openspec/specs/<área>/spec.md` | Specs vigentes del sistema: `core`, `ui`, `i18n`, `build`. Son la fuente de verdad del comportamiento actual. |
| `openspec/changes/<nombre>/` | Changes en curso: `proposal.md`, `design.md`, `tasks.md` y `specs/` (deltas sobre las specs principales). |
| `openspec/changes/archive/` | Changes ya terminados y archivados. |
| `CLAUDE.md` | Instrucciones del proyecto para Claude Code. |
| `.claude/skills/`, `.claude/commands/opsx/` | Skills y comandos `/opsx:*` para Claude Code. |
| `.agents/skills/`, `.agents/workflows/` | Skills y workflows `/opsx-*` para Antigravity. |
| `.claude/settings.json` | Hook que verifica las traducciones tras cada edición de `translations.py`. |

### Flujo para una nueva funcionalidad

Los comandos se escriben en el chat del asistente. En **Claude Code** se usan con dos puntos (`/opsx:propose`) y en **Antigravity** con guion (`/opsx-propose`).

#### 0. Partir de una rama limpia

```bash
git checkout main
git pull
git checkout -b feature/nombre-de-la-funcionalidad
```

#### 1. Explorar la idea (opcional)

```
/opsx:explore ¿cómo podríamos permitir descargar solo los videos de un rango de fechas?
```

Sirve para analizar el código, comparar alternativas y aclarar requisitos **sin escribir nada**. Útil cuando la idea todavía no está clara.

#### 2. Proponer el change

```
/opsx:propose añadir filtro por rango de fechas antes de descargar
```

Crea `openspec/changes/<nombre>/` con:

- `proposal.md`: qué se hace, por qué, impacto para el usuario y lo que queda fuera (non-goals).
- `design.md`: componentes afectados, flujo de datos, manejo de hilos y errores, y **las claves de traducción nuevas con sus valores en es, en y pt**.
- `specs/<área>/spec.md`: requisitos y escenarios añadidos o modificados (deltas).
- `tasks.md`: tareas atómicas con su paso de verificación.

#### 3. Revisar y ajustar la propuesta

Lee los artefactos generados antes de implementar. Si algo no encaja, pide cambios:

```
/opsx:update el filtro debe estar en la barra lateral, no en el header
```

Comprueba que el change es válido:

```bash
openspec list                      # changes activos
openspec show <nombre>             # ver el change
openspec validate <nombre>         # validar formato de specs y artefactos
```

#### 4. Implementar

```
/opsx:apply <nombre>
```

La IA recorre `tasks.md`, implementa cada tarea y la marca como `[x]`. Si se interrumpe, vuelve a ejecutar el mismo comando para continuar. Reglas que se aplican siempre (definidas en `openspec/config.yaml` y `CLAUDE.md`):

- Las llamadas de red, descargas y carga de miniaturas van en hilos (`threading.Thread`); nunca se bloquea la UI.
- Ningún texto visible se escribe directamente en el código: se usa `t("area.clave")`.
- **Toda clave nueva o modificada se añade en `es`, `en` y `pt`** en `magoloader/i18n/translations.py`, con los mismos `{placeholders}`.

#### 5. Verificar

```bash
python scripts/check_i18n.py               # traducciones completas en es, en y pt
python -m unittest discover -s tests       # tests
python main.py                             # prueba manual de la funcionalidad
```

`check_i18n.py` falla si a algún idioma le falta una clave, si hay traducciones vacías o si los `{placeholders}` no coinciden. En Claude Code se ejecuta automáticamente después de cada edición de `translations.py`.

#### 6. Archivar el change

```
/opsx:archive <nombre>
```

Fusiona los deltas de `specs/` en `openspec/specs/` y mueve el change a `openspec/changes/archive/`. Si solo quieres actualizar las specs principales sin archivar todavía, usa `/opsx:sync <nombre>`.

#### 7. Changelog, commit y Pull Request

1. Añade la entrada en `CHANGELOG.md` (sección `Added`, `Changed` o `Fixed`).
2. Haz commit incluyendo el código **y** los cambios de `openspec/`:

   ```bash
   git add .
   git commit -m "feat: filtro por rango de fechas"
   git push -u origin feature/nombre-de-la-funcionalidad
   ```

3. Abre un Pull Request hacia `main`. Si la funcionalidad va en una nueva versión, sigue la sección **Crear una nueva versión** más abajo.

### Resumen rápido

| Paso | Claude Code | Antigravity |
|------|-------------|-------------|
| Explorar | `/opsx:explore` | `/opsx-explore` |
| Proponer | `/opsx:propose` | `/opsx-propose` |
| Ajustar | `/opsx:update` | `/opsx-update` |
| Implementar | `/opsx:apply` | `/opsx-apply` |
| Sincronizar specs | `/opsx:sync` | `/opsx-sync` |
| Archivar | `/opsx:archive` | `/opsx-archive` |

### Mantener OpenSpec actualizado

Tras actualizar la CLI (`npm install -g @fission-ai/openspec@latest`), regenera las skills y comandos de los asistentes:

```bash
openspec update
```

Para añadir otro asistente de IA al proyecto: `openspec init --tools <herramienta>` (por ejemplo `claude`, `antigravity`, `cursor`).

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

