# Design

## Context

See `proposal.md` for the motivation, and `specs/ui/spec.md` and `specs/core/spec.md` for the requirements.

### Current state

- `MagoLoaderApp` (`magoloader/ui/app.py`, about 390 lines) does everything in one class:
  - builds the layout: `Header`, `Sidebar`, video grid, `PaginationBar`, `Footer`;
  - owns all state: `profile_info`, `video_entries`, `selected_urls`, `current_page`, `save_dir`, running flags;
  - runs the UI update queue (`pending_ui_updates`, polled every 200 ms with `after`);
  - runs background threads (`_run_in_thread`) and maps errors to translated messages.
- Components (`magoloader/ui/components/`) receive callbacks and expose setters. They never touch app state directly. That's a good base to build on.
- `Header` hardcodes the app title label next to the username entry.
- `Sidebar` hardcodes the save-folder section.
- `Footer` hardcodes the `footer.download` text with a `{n}` count.
- `VideoCard` always shows a selection checkbox.
- `download_video(url, save_dir)` returns nothing and reports no progress.
- `TikTokExtractor` only extracts profiles.
- `messagebox.showerror("Error", ...)` uses an untranslated title.

## Goals / Non-Goals

**Goals:**
- Turn `MagoLoaderApp` into a thin shell: a window, a title, a `CTkTabview`, the UI queue loop, and shared services.
- Each tab is a self-contained `CTkFrame` that only receives shared services. Adding a third tab means writing one new file and one line in the shell.
- Reuse the same components in both tabs: input bar, folder picker, footer and video card, instead of duplicating them.
- Keep the Profile tab's behavior identical. Moving code is fine; behavior changes are not.

**Non-Goals:**
- Changing the profile flow logic or adding features to the Profile tab. The only cleanup allowed is removing the redundant `set_analyzing(True)` call in `on_done`, which has no visible effect.
- An MVC or presenter layer, or a dependency-injection framework. Plain constructor arguments are enough at this size.
- Runtime language switching. Text is resolved with `t()` when widgets are created, as it is now.

## Decisions

### 1. Component hierarchy

```
MagoLoaderApp (ctk.CTk)                       ui/app.py — thin shell
├── title label  t("app.title")
├── CTkTabview (accent-styled)
│   ├── tab t("tabs.profile") → ProfileTab   ui/tabs/profile_tab.py
│   │   ├── InputBar (username)                ui/components/input_bar.py   [new, from Header]
│   │   ├── Sidebar                            ui/components/sidebar.py
│   │   │   └── SaveFolderPicker               ui/components/save_folder_picker.py [new, from Sidebar]
│   │   ├── select-page / select-all buttons
│   │   ├── CTkScrollableFrame → VideoCard × 12
│   │   ├── PaginationBar
│   │   └── Footer (batch label "footer.download" {n})
│   └── tab t("tabs.url") → UrlTab           ui/tabs/url_tab.py           [new]
│       ├── InputBar (URL, "url.fetch"/"url.fetching")
│       ├── side panel (COLOR_CARD, 260 px)
│       │   └── SaveFolderPicker
│       ├── preview area (COLOR_CARD)
│       │   ├── hint label t("url.empty_hint")   (empty state)
│       │   └── VideoCard(selectable=False)       (after fetch)
│       └── Footer (button text "url.download")
└── shared services passed to each tab
    ├── TaskRunner                             ui/task_runner.py            [new]
    └── SaveDirState                           ui/state.py                  [new]
```

**Why:**
- The profile flow already moves cleanly as one unit, so it becomes `ProfileTab` with its current methods mostly unchanged.
- Both tabs need the same "entry + action button with a busy label" pattern. The profile header becomes a generic `InputBar`, configured by placeholder, button text and busy text.
- `Header` stays as a thin subclass of `InputBar` with `get_username()` and `set_analyzing()`, so imports and calls in the Profile code stay the same.
- The app title moves to the window level above the tabs, because it belongs to the app, not to one tab.

**Alternative considered:** keep `Header` and duplicate a URL header. Rejected because it repeats the same styling and busy-state logic.

### 2. Shared services

**`TaskRunner(root, queue)`** extracts `_run_in_thread`, `_process_ui_queue`, `_show_error` and `_show_info` from the current app:
- `post(callback)`: queues a UI callback. This is the only safe way for background threads to touch widgets.
- `run(target, on_done=None, error_message=None)`: runs `target` in a daemon `threading.Thread`.
  - If it fails, the error is mapped to a message in this order: SSL → `error.ytdlp_ssl`; then `error_message(exc)` if one was given; otherwise outdated extractor → `err_ytdlp_outdated`, else `str(exc)`.
  - The caller's mapper runs before the outdated check because yt-dlp's "No video formats found" error (image/slideshow posts) also contains "please report". Without that order, the URL tab would wrongly suggest updating yt-dlp. The URL tab's mapper returns `err_ytdlp_outdated` only for genuine extractor failures and `error.video_unavailable` for everything else.
  - The message is shown on the UI thread through `show_error`.
  - `on_done` is always posted afterwards.
- `show_error(msg)` / `show_info(msg)`:
  - Error popups use the new translated title `dialog.error_title` instead of the hardcoded `"Error"`.
  - Info popups keep `app.title`.
  - Errors are still tracked with `analytics.track_error`.
- The shell keeps the `after(200, ...)` polling loop and owns the single `queue.Queue`. Tabs never create threads or queues themselves.

**`SaveDirState(initial)`** is a tiny observable:
- `get()`
- `set(path)`: creates the folder and notifies subscribers.
- `subscribe(callback)`

Each tab's `SaveFolderPicker` subscribes to it, so a change in one tab updates the label in both. Downloads read `save_dir_state.get()` when they start.

**Alternative considered:** a global module variable. Rejected because it's harder to test, and subscribers would still be needed to refresh the labels.

### 3. Reusable component changes (backward compatible)

| Component | Change |
|-----------|--------|
| `InputBar` (new) | `InputBar(master, placeholder, button_text, busy_text, on_submit, entry_width=None)`. The entry expands to fill the row when `entry_width` is `None`. Pressing Enter submits. `get_value()`, `set_busy(bool)`, `bind_change(callback)` (uses the `<KeyRelease>` event, needed for "editing the URL invalidates the preview"). |
| `Header` | Becomes `class Header(InputBar)` and keeps `get_username()` / `set_analyzing()`. The title label is removed. |
| `SaveFolderPicker` (new) | "Save location" title, truncated path label and "Browse..." button, taken from `Sidebar`. Opens `filedialog.askdirectory` and calls `SaveDirState.set`. |
| `Sidebar` | Builds a `SaveFolderPicker` instead of its own folder widgets. `set_save_dir` is no longer needed because the picker subscribes to the state. |
| `Footer` | New optional `button_text: str \| None`. If it's `None`, it keeps the current `footer.download` `{n}` text. New `set_button_text(text)`. `set_progress` and `set_download_enabled` are reused as they are. |
| `VideoCard` | New `selectable: bool = True`. When `False`, the checkbox isn't created, clicking the thumbnail does nothing, and `var`/`on_toggle` may be `None`. |

### 4. Core additions

- **`utils.normalize_tiktok_video_url(text) -> str | None`:**
  - Uses `urllib.parse` plus regular expressions. No network.
  - Adds `https://` if the scheme is missing.
  - Compares the host exactly against an allow-list:
    - `tiktok.com`, `www.tiktok.com`, `m.tiktok.com` with path `/@user/video/<digits>`, `/t/<code>` or `/v/<digits>.html`;
    - `vm.tiktok.com` and `vt.tiktok.com` with path `/<code>/`.
  - Returns the normalized URL, or `None` if the input is rejected.
  - Exact host matching (not `"tiktok.com" in url`) rejects look-alike domains.
- **`BaseExtractor.extract_video(url) -> VideoEntry`:** new abstract method. `TikTokExtractor.extract_video`:
  - calls `extract_info(url, download=False)` without `extract_flat`, which resolves short links;
  - uses the same 3-attempt retry as `extract`;
  - raises `RuntimeError` if the result is a playlist or has no id;
  - builds a `VideoEntry` from `webpage_url`, `id`, `title`, `duration`, `thumbnail`/`thumbnails` (reusing `_first_thumbnail_url`) and `uploader`.
- **`VideoEntry`** gets an optional `uploader: Optional[str] = None`. Existing code that builds it isn't affected.
- **`download_video(url, save_dir, outtmpl=None, on_progress=None) -> str | None`:**
  - If `on_progress` is given, it registers a yt-dlp `progress_hook`:
    - while downloading, it reports `downloaded_bytes / (total_bytes or total_bytes_estimate)`, clamped to 0..1, and skips the update if the total is unknown;
    - when finished, it reports `1.0`.
  - It switches to `extract_info(url, download=True)` to return the final path, taken from `requested_downloads[0]["filepath"]` with `prepare_filename(info)` as a fallback.
  - The profile batch loop ignores the return value, so it's unchanged.
- **`Analytics.track_url_download()`** sends the `url_download` event through the existing `track_event`.

### 5. UrlTab data flow and UI states

```
[idle] ─Fetch/Enter─► validate locally
   │                    ├─ empty   → show_error(error.no_url)         → [idle]
   │                    ├─ invalid → show_error(error.invalid_url)    → [idle]
   │                    └─ ok      → [fetching]
[fetching]  InputBar busy ("url.fetching"), Download disabled
   runner.run(extract_video, error_message=→ error.video_unavailable)
   ├─ success → post: store entry, replace preview with VideoCard(selectable=False),
   │            Download enabled                                     → [ready]
   └─ error   → popup, keep/clear preview hidden                     → [idle]
[ready] ─edit URL─► clear entry, Download disabled                   → [idle]
[ready] ─Download─► [downloading]
[downloading] Fetch + Download disabled, Footer button text "url.downloading",
   runner.run(download_video(entry.url, save_dir_state.get(), on_progress=post→footer.set_progress))
   ├─ success → post: show_info(url.saved_to, path=...), track_url_download → [ready]
   └─ error   → popup                                                → [ready]
   on_done → re-enable buttons, restore "url.download" text
```

- **Thread safety:**
  - Background threads only call `runner.post(...)`.
  - All widget changes happen in callbacks run from the UI-thread queue loop. This includes progress updates, which are posted with the fraction captured as a lambda default (`lambda p=p: ...`).
  - `VideoCard` already loads thumbnails in a thread and pushes them back through `ui_update_queue`.
- **Running flags:**
  - `UrlTab` has its own `_fetch_running` and `_download_running`, separate from `ProfileTab._analysis_running` and `_download_running`. That's why both tabs can work at the same time.
  - A fetch result that arrives after the user has edited the URL is dropped. The tab compares a request token, the URL string it captured, with the URL that is current.
- **Fallbacks:**
  - Missing title → `video.no_title`.
  - Missing thumbnail → `VideoCard`'s existing oEmbed lookup, then a placeholder.
  - Unknown total size → progress jumps to 100% when the download finishes.

### 6. Tab view styling

- `CTkTabview` uses the existing theme tokens:
  - `fg_color=COLOR_BG`;
  - `segmented_button_selected_color=COLOR_ACCENT` and `segmented_button_selected_hover_color=COLOR_ACCENT_HOVER`;
  - `segmented_button_unselected_color=COLOR_CARD`;
  - `text_color=COLOR_TEXT`.
- Tabs are created in a fixed order (Profile, then Video URL), and Profile is selected at startup.
- The tab names come from `t()`, so they are fixed for the session, which matches how the rest of the UI works.

### 7. Translation keys (new)

All keys are added to `es`, `en` and `pt` in `magoloader/i18n/translations.py`. Existing keys are reused where they fit: `sidebar.save_location`, `sidebar.browse`, `footer.progress`, `video.no_title`, `error.ytdlp_ssl`, `err_ytdlp_outdated`, `info.download_finished`.

| Key | es | en | pt |
|-----|----|----|----|
| `tabs.profile` | Perfil | Profile | Perfil |
| `tabs.url` | URL de video | Video URL | URL do vídeo |
| `url.placeholder` | Pega el enlace del video de TikTok | Paste the TikTok video link | Cole o link do vídeo do TikTok |
| `url.fetch` | Buscar | Fetch | Buscar |
| `url.fetching` | Buscando... | Fetching... | Buscando... |
| `url.empty_hint` | Pega un enlace de TikTok y pulsa Buscar para ver el video. | Paste a TikTok link and press Fetch to preview the video. | Cole um link do TikTok e clique em Buscar para ver o vídeo. |
| `url.download` | Descargar video | Download video | Baixar vídeo |
| `url.downloading` | Descargando... | Downloading... | Baixando... |
| `url.saved_to` | Video guardado en:\n{path} | Video saved to:\n{path} | Vídeo salvo em:\n{path} |
| `error.no_url` | Escribe o pega la URL de un video de TikTok. | Enter or paste a TikTok video URL. | Digite ou cole a URL de um vídeo do TikTok. |
| `error.invalid_url` | El enlace no es una URL válida de un video de TikTok. | This link is not a valid TikTok video URL. | O link não é uma URL válida de vídeo do TikTok. |
| `error.video_unavailable` | No se pudo obtener el video. Puede ser privado, haber sido eliminado o el enlace es incorrecto. | Could not get the video. It may be private, deleted, or the link is wrong. | Não foi possível obter o vídeo. Ele pode ser privado, ter sido excluído ou o link está incorreto. |
| `dialog.error_title` | Error | Error | Erro |

`url.saved_to` uses the `{path}` placeholder in all three languages, which `scripts/check_i18n.py` checks.

## Risks / Trade-offs

- **[Risk] The refactor accidentally changes Profile tab behavior.**
  → Code is moved, not rewritten. Task 3 is a dedicated manual regression check of the full profile flow (analyze, paginate, select page/all, browse, batch download).
- **[Risk] Switching from `download()` to `extract_info(download=True)` changes how yt-dlp behaves.**
  → Both run the same pipeline with the same options. The return value is only used by the URL tab. The batch download is verified manually.
- **[Risk] Short links (`vm.`/`vt.`) need a redirect that sometimes fails or is region-blocked.**
  → yt-dlp follows the redirect during extraction. A failure falls into `error.video_unavailable`, or the SSL/outdated messages when those apply.
- **[Risk] The window's minimum height (600 px) gets tighter because the tab bar and title take about 70 px.**
  → Check at the minimum size that the profile grid, pagination and footer are still visible. If not, reduce the outer padding (16 → 12) rather than changing `WINDOW_MINSIZE`.
- **[Trade-off] Running a URL download and a profile batch at the same time doubles network use and may write to the same folder at once.**
  → Accepted. The files have different names, and yt-dlp skips a file that already exists. Serializing downloads is out of scope.
- **[Trade-off] An extra `extract_info` call in Fetch before Download means two requests per video.**
  → Accepted: the preview is the confirmation step the user chose. The download reuses the canonical URL returned by the fetch.

## Migration Plan

No data or config migration is needed. Rollback means reverting the change's commits; nothing is persisted in a new way.
