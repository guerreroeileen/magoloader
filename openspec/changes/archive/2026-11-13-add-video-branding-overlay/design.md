# Design

## Context

- Downloads go through `download_video(url, save_dir, outtmpl=None, on_progress=None)` in `magoloader/core/downloader.py`, which returns the saved path. The Profile tab calls it in a loop (and silently skips failed videos); the Video URL tab calls it once with `on_progress`.
- All background work uses `TaskRunner.run(target, on_done, error_message)`; widget updates go through `TaskRunner.post` and are drained by the Tk loop every 200 ms.
- Shared cross-tab state already follows one pattern: `SaveDirState` (`get`/`set`/`subscribe`) in `magoloader/ui/state.py`, consumed by `SaveFolderPicker` in both tabs.
- The Profile `Sidebar` is a fixed 260 px wide `CTkFrame` with `pack_propagate(False)`; the Video URL tab builds its own 260 px side frame. Neither scrolls today.
- The project has Pillow but no FFmpeg. yt-dlp is not configured with any post-processor, so it does not need FFmpeg today.
- The app ships as a `--onefile --noconsole` PyInstaller executable.

Requirements are in `specs/branding`, `specs/core`, `specs/ui` and `specs/build`.

## Goals / Non-Goals

**Goals:**
- One rendering path for all overlay elements, so the result looks the same regardless of FFmpeg build features (fonts, `drawtext`).
- Keep `download_video` backward compatible: callers that pass no branding get byte-for-byte the same behavior.
- Keep all Tk access on the main thread; the worker only receives an immutable snapshot of the settings.

**Non-Goals:**
- Hardware encoding, encoder presets exposed to the user, or keeping the original codec when branding.
- Reusing the overlay for images or GIFs.

## Decisions

### 1. Render the overlay with Pillow, composite with FFmpeg `overlay`

`render_overlay(width, height, options) -> PIL.Image (RGBA)` builds one transparent PNG at the exact video size containing the gradient, the logo and the text. FFmpeg then composites it once:

```
ffmpeg -y -i <video> -i <overlay.png>
  -filter_complex "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]"
  -map "[v]" -map "0:a?" -c:v libx264 -preset veryfast -crf 18
  -c:a copy -movflags +faststart -progress pipe:1 -nostats <tmp.mp4>
```

- No `scale` filter anywhere, so width/height are preserved by construction; `overlay` keeps the main input's size and frame rate.
- `-map 0:a?` copies audio when present and is a no-op when absent.
- **Alternatives:** FFmpeg `drawtext` + `geq` gradient — rejected: needs a font file path on every machine, escaping of user text, and `geq` is slow. Frame-by-frame compositing in Python (Pillow/numpy) — rejected: far slower and needs a decoder anyway.

### 2. Overlay geometry (all relative to the frame)

With `W`, `H` the video size and `base = min(W, H)`:

| Element | Rule |
|---|---|
| Gradient band | bottom `0.35 * H` rows. Alpha at row position `p` (0 at band top, 1 at bottom) = `0.92 * smoothstep(p)` where `smoothstep(p) = p*p*(3-2p)`. Drawn as a 1 px wide column, then resized to `W` (fast). |
| Padding | `pad = round(0.035 * base)` |
| Logo | fit inside `0.20 * W` × `0.12 * H` box keeping aspect ratio (`Image.thumbnail` semantics but allowed to scale up to the box), placed at `(W - pad - lw, pad)`, alpha-composited (RGBA preserved, other modes converted to RGBA). |
| Name | white, bold, start size `0.045 * base`; shrink by 1 px steps until text width ≤ `W - 2*pad` (min 10 px); if it still does not fit at 10 px, the end is cut with `…`. Centered horizontally; text bottom at `H - 1.6*pad`. Shadow: same text in black at 50% alpha offset by `max(1, size//18)` px, drawn first. |

Font: try `arialbd.ttf`, `segoeuib.ttf` (Windows), then `DejaVuSans-Bold.ttf`; fall back to `ImageFont.load_default(size=...)` (needs Pillow ≥ 10.1). The text is drawn with Pillow, so user text needs no escaping.

These constants live at the top of `magoloader/core/branding.py` so the look can be tuned without touching the logic. The reference image is the visual target; values are a starting point to check in task 6.

### 3. Getting the video size

`probe_video(path) -> VideoInfo(width, height, duration, has_audio)` runs `ffmpeg -i <path>` and parses stderr (`Stream #...: Video: ..., 720x1280` and `Duration: 00:00:12.34`). If the stream has rotation side data (`rotate: 90/270` or `displaymatrix: rotation of -90.00 degrees`), width and height are swapped because FFmpeg auto-rotates on decode. yt-dlp's `info["width"/"height"]` is not trusted because it describes the selected format before download and may be missing.
**Alternative:** bundle `ffprobe` — rejected, `imageio-ffmpeg` only ships `ffmpeg`.

### 4. FFmpeg source: `imageio-ffmpeg`

`imageio_ffmpeg.get_ffmpeg_exe()` returns the bundled binary path (works in the PyInstaller bundle when the package is collected with `--collect-all=imageio_ffmpeg`). Wrapped in `magoloader/core/ffmpeg.py::get_ffmpeg_path()` so it can be mocked and so a system `ffmpeg` on `PATH` is the fallback if the import fails. Every subprocess call uses `creationflags=subprocess.CREATE_NO_WINDOW` on Windows (no console flash in `--noconsole` builds) and `stdin=DEVNULL`.

### 5. Data model and API

In `magoloader/core/branding.py`:

```python
@dataclass(frozen=True)
class BrandingOptions:
    color: str            # normalized "#RRGGBB"
    logo_path: Optional[str] = None
    name: str = ""

class BrandingError(RuntimeError):
    def __init__(self, message: str, video_path: str): ...

def normalize_hex_color(text: str) -> Optional[str]: ...
def load_logo(path: str) -> Image.Image: ...           # raises ValueError
def render_overlay(width: int, height: int, options: BrandingOptions) -> Image.Image: ...
def apply_branding(video_path: str, options: BrandingOptions,
                   on_progress: Optional[Callable[[float], None]] = None) -> str: ...
```

`apply_branding` flow: probe → render overlay to a temp PNG (`tempfile.mkstemp`) → run FFmpeg into `<stem>.branding.tmp.mp4` in the same folder → on exit code 0 and non-empty output, `os.replace(tmp, video_path)` → delete PNG. Any failure deletes the tmp files and raises `BrandingError(msg, video_path)`; the original file is untouched until the atomic replace. Progress parses `out_time_ms=` lines from `-progress pipe:1` against the probed duration (clamped 0..1; 1.0 at `progress=end`). stderr is drained in a thread to avoid pipe deadlock and kept (last ~4 KB) for the error message.

The output is always `.mp4` (H.264/AAC-or-copied audio). TikTok downloads are already `.mp4`; if yt-dlp ever saved another extension, the branded file is written next to it with `.mp4` and the original removed, and that new path is returned.

`download_video(..., branding: Optional[BrandingOptions] = None)`:
- `None` → current code path unchanged.
- Set → the download runs with yt-dlp `overwrites=True`, so re-downloading a video that is already in the folder (possibly already branded) fetches the original again instead of branding it twice. yt-dlp progress maps to `0.0–0.6`, branding to `0.6–1.0` on the same `on_progress`; returns the branded path. An extra optional `on_stage: Callable[[str], None]` is called with `"branding"` when the second step starts (used by the URL tab to change the button text).

### 6. Settings state and persistence

- `magoloader/core/branding_settings.py`: `BrandingSettings` dataclass (`enabled: bool`, `color_text: str`, `logo_path: Optional[str]`, `name: str`), `load_settings(path=BRANDING_FILE) -> BrandingSettings` (never raises; invalid fields fall back to defaults, missing logo file → `None`), `save_settings(settings, path)` (write to `.tmp` then `os.replace`), `store_logo_copy(src) -> str` (validates with `load_logo`, saves as PNG to `~/.magoloader/branding_logo.png`, returns that path).
- `color_text` stores the raw text the user typed so an in-progress invalid value is shown again; `to_options() -> Optional[BrandingOptions]` returns `None` when disabled and raises `ValueError` when enabled with an invalid color.
- New constants in `magoloader/constants.py`: `APP_DATA_DIR = ~/.magoloader`, `BRANDING_FILE`, `BRANDING_LOGO_FILE`, `DEFAULT_BRANDING_COLOR = "#0000FF"`.
- `BrandingState` in `magoloader/ui/state.py`, same shape as `SaveDirState`: `get() -> BrandingSettings`, `update(**changes)` (replaces the frozen dataclass, saves, notifies subscribers with the new value), `subscribe(cb)`, plus `set_locked(bool)` / `subscribe_lock(cb)` used to disable both panels during downloads. Saving happens on the UI thread; the file is tiny. Name/color edits are saved debounced (500 ms via `after`) to avoid a write on each keystroke.

### 7. UI component hierarchy

```
MagoLoaderApp
 ├─ BrandingState(load_settings())            # created next to SaveDirState
 ├─ ProfileTab(…, branding_state)
 │   └─ Sidebar  → CTkScrollableFrame body
 │        ├─ profile card
 │        ├─ SaveFolderPicker
 │        └─ BrandingPanel(branding_state)
 └─ UrlTab(…, branding_state)
     └─ side column → CTkScrollableFrame
          ├─ SaveFolderPicker
          └─ BrandingPanel(branding_state)

BrandingPanel (CTkFrame, border COLOR_ACCENT, corner_radius 10)
 ├─ title label  (branding.title, small caps style, COLOR_TEXT_DIM)
 ├─ CTkCheckBox  (branding.enable)
 └─ body frame   (pack/pack_forget on toggle)
     ├─ label branding.color
     ├─ row: swatch CTkButton(36x28, fg=color) + CTkEntry(hex)
     ├─ label branding.logo
     ├─ row: CTkButton(sidebar.browse) + CTkButton(branding.logo_remove) + preview CTkLabel(48x48)
     ├─ label branding.name
     └─ CTkEntry(placeholder branding.name_placeholder)
```

- Swatch click → `tkinter.colorchooser.askcolor(initialcolor=..., title=t("branding.pick_color"))`.
- Logo browse → `filedialog.askopenfilename(title=t("branding.logo_dialog"), filetypes=[(t("branding.image_files"), "*.png *.jpg *.jpeg *.webp")])` → `store_logo_copy` on the UI thread (a single small image; acceptable) → on `ValueError` show `error.invalid_logo`.
- The name field does not use a `textvariable` (CTkEntry ignores `placeholder_text` when one is set); it listens to key, paste and focus-out events instead.
- When the logo is removed, the inner Tk label's image is cleared explicitly before the old `CTkImage` reference is dropped (CTkLabel does not clear it with `image=None`, which would raise "pyimage doesn't exist").
- `BrandingPanel` updates its widgets from subscriber callbacks. To avoid feedback loops, it skips writing to an entry whose current text already equals the new value, and suppresses its own change handler while applying external updates (`self._applying = True`).
- `TaskRunner` is passed to the panel only for `show_error`.

### 8. Download flow changes

On click, on the UI thread, each tab:
1. calls `branding_state.get().to_options()`; on `ValueError` → `show_error(t("error.invalid_hex"))` and returns;
2. calls `branding_state.set_locked(True)`; `on_done` calls `set_locked(False)` (a counter, so two tabs downloading at once unlock only when both finish);
3. passes the frozen `BrandingOptions` (or `None`) into the worker closure.

- **URL tab:** `on_stage("branding")` posts `footer.set_button_text(t("branding.applying"))`. `BrandingError` is caught inside `do_download`, `track_url_download()` still runs, and it posts `show_info(t("info.saved_unbranded", path=e.video_path))` instead of raising (the download did succeed).
- **Profile tab:** per video, progress becomes `(i + fraction) / total` using `on_progress`. `BrandingError` increments `branding_failures`; other exceptions keep today's behavior (skipped). The final message is `info.download_finished` when `branding_failures == 0`, else `info.download_finished_unbranded` with `{n}`.

### 9. Translation keys

| Key | es | en | pt |
|---|---|---|---|
| `branding.title` | PERSONALIZACIÓN DE VIDEO (Opcional) | VIDEO CUSTOMIZATION (Optional) | PERSONALIZAÇÃO DE VÍDEO (Opcional) |
| `branding.enable` | Personalizar contenido | Personalize content | Personalizar conteúdo |
| `branding.color` | Color del degradado (HEX) | Gradient color (HEX) | Cor do degradê (HEX) |
| `branding.pick_color` | Elegir color del degradado | Choose gradient color | Escolher cor do degradê |
| `branding.logo` | Logo (imagen) | Logo (image) | Logo (imagem) |
| `branding.logo_dialog` | Seleccionar logo | Select logo | Selecionar logo |
| `branding.image_files` | Imágenes | Images | Imagens |
| `branding.logo_remove` | Quitar | Remove | Remover |
| `branding.no_logo` | Sin logo | No logo | Sem logo |
| `branding.name` | Nombre de página (texto) | Page name (text) | Nome da página (texto) |
| `branding.name_placeholder` | @MiPagina | @MyPage | @MinhaPagina |
| `branding.applying` | Aplicando personalización... | Applying customization... | Aplicando personalização... |
| `error.invalid_hex` | El color debe ser un código HEX válido, por ejemplo #0000FF. | The color must be a valid HEX code, for example #0000FF. | A cor deve ser um código HEX válido, por exemplo #0000FF. |
| `error.invalid_logo` | No se pudo abrir la imagen. Usa un archivo PNG, JPG o WEBP. | Could not open the image. Use a PNG, JPG or WEBP file. | Não foi possível abrir a imagem. Usa um ficheiro PNG, JPG ou WEBP. |
| `info.saved_unbranded` | El video se descargó, pero no se pudo aplicar la personalización. Se guardó sin personalizar en:\n{path} | The video was downloaded, but the customization could not be applied. It was saved without customization to:\n{path} | O vídeo foi descarregado, mas não foi possível aplicar a personalização. Foi guardado sem personalização em:\n{path} |
| `info.download_finished_unbranded` | Descarga finalizada. {n} video(s) se guardaron sin personalizar porque no se pudo aplicar la personalización. | Download finished. {n} video(s) were saved without customization because it could not be applied. | Download concluído. {n} vídeo(s) foram guardados sem personalização porque não foi possível aplicá-la. |

The Portuguese texts follow the existing `pt` catalog's style (`Descarregar`, `Seleciona`). `sidebar.browse` is reused for the logo "Browse..." button.

### 10. Packaging

- `requirements.txt`: add `imageio-ffmpeg>=0.5.1`; raise `Pillow>=10.1.0`.
- `build.py`: add `--collect-all=imageio_ffmpeg`. `MagoLoader.spec`: add the matching `collect_all('imageio_ffmpeg')` block.

## Risks / Trade-offs

- [Re-encoding lowers quality slightly and takes time] → `crf 18` + `veryfast` keeps it visually lossless for TikTok sources; progress is shown; only done when the user opts in.
- [Odd video dimensions break `yuv420p` H.264] → TikTok output is even-sized; if the probe returns odd width/height, encode with `-pix_fmt yuv444p` + `-profile:v high444` instead of cropping, so the size is still preserved.
- [Larger executable (+30–80 MB) and slower one-file startup] → accepted by the user; documented in the CHANGELOG.
- [Parsing `ffmpeg -i` output is brittle across FFmpeg versions] → the FFmpeg version is pinned by the bundled package; the parser is covered by unit tests with sample stderr (including rotated streams).
- [Antivirus may flag spawning a bundled exe from the temp folder] → no mitigation beyond the existing PyInstaller signing situation; a failure surfaces as `BrandingError` and the unbranded file is kept.
- [User text with emoji or scripts missing from Arial] → missing glyphs render as boxes; acceptable for this version.
- [Two tabs editing the same state] → all edits happen on the UI thread; workers only see frozen snapshots taken at download start.

## Migration Plan

No data migration. The settings file is created on first change. Rollback = revert the change; a leftover `~/.magoloader/branding.json` is ignored by older versions.
