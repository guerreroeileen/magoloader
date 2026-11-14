# Proposal

## Why

Users who republish TikTok videos for a page, creator or media outlet want their own brand on the video: a soft color gradient at the bottom, their logo in the top-right corner and the page name over the gradient. Today they have to edit each video in a separate tool after downloading it. Adding an optional "Personalize content" step to the download flow lets them brand videos in one step, at the original resolution.

## What Changes

- New optional **video customization panel** in **both tabs** (Profile and Video URL). It holds a "Personalize content" checkbox and, when checked:
  - a HEX color field (`#RRGGBB`) with a color swatch that opens the native color picker,
  - a logo picker (PNG/JPG/WEBP) with a small preview and a "Remove" button,
  - a text field for the page, creator or media outlet name.
- The panel's values are **shared** between both tabs (same pattern as the save folder) and **remembered between sessions** in `~/.magoloader/branding.json`. The chosen logo is copied to `~/.magoloader/` so it keeps working if the original file moves.
- When the option is checked, every downloaded video is branded after the download finishes:
  - a smooth gradient in the chosen color at the bottom (transparent at the top of the band, almost solid at the bottom edge), as in the reference image,
  - the logo in the top-right corner with padding, scaled relative to the video size,
  - the name centered at the bottom, in white bold text over the gradient.
- The video is **never resized or cropped**: the output has the same width, height and frame rate as the download, and the audio is copied unchanged. Only the branded file is kept, with the same file name as today.
- When the option is unchecked, the download works exactly as it does now (no extra processing, no FFmpeg call).
- If branding fails for a video, the unbranded download is kept and the user gets a translated message. Batch downloads in the Profile tab report how many videos could not be branded.
- **New dependency:** `imageio-ffmpeg`, which ships an FFmpeg binary. It is bundled into the PyInstaller executable, so users do not have to install FFmpeg.
- New user-facing text (panel labels, placeholders, color and logo dialogs, progress text, validation and failure messages) will be added and translated to **es, en and pt**.

### Non-goals

- No video editing beyond these three overlay elements (no trimming, no repositioning, no per-video settings, no fonts or text color choice; the text is always white).
- No change to how videos are found or downloaded by yt-dlp, and no re-encoding when customization is off.
- No live video preview of the result inside the app (only the logo thumbnail and color swatch are shown).
- TikTok photo/slideshow posts are out of scope, as they are for downloads today.

### Performance and threading

- Branding re-encodes the video with FFmpeg (H.264), which takes noticeably longer than the download alone (a few seconds for a typical TikTok video, more for long or 4K videos). It runs in the same background thread as the download, never on the Tk main loop, and reports progress to the footer bar.
- The FFmpeg subprocess runs with no console window (the app is built with `--noconsole`).
- The executable grows by the size of the bundled FFmpeg binary (roughly 30–80 MB).

## Capabilities

### New Capabilities
- `branding`: video customization overlay: settings (color, logo, name, enabled flag), validation, persistence, overlay rendering at the source resolution and applying it to a downloaded video with FFmpeg.

### Modified Capabilities
- `core`: video downloads can optionally apply branding after downloading, keeping the unbranded file if branding fails.
- `ui`: new shared customization panel in the Profile and Video URL tabs, and download flows that validate and pass the branding settings.
- `build`: the PyInstaller bundle must include the FFmpeg binary from `imageio-ffmpeg`.

## Impact

- **New code:** `magoloader/core/branding.py` (options model, HEX validation, overlay rendering with Pillow, FFmpeg processing), `magoloader/core/branding_settings.py` (load/save JSON), `magoloader/ui/components/branding_panel.py`, `BrandingState` in `magoloader/ui/state.py`.
- **Changed code:** `magoloader/core/downloader.py` (optional `branding` argument), `magoloader/ui/components/sidebar.py` (hosts the panel and becomes scrollable so it fits at 900x600), `magoloader/ui/tabs/profile_tab.py`, `magoloader/ui/tabs/url_tab.py`, `magoloader/ui/app.py` (creates the shared `BrandingState`), `magoloader/i18n/translations.py`.
- **Dependencies and build:** `requirements.txt` (`imageio-ffmpeg`, `Pillow>=10.1` for sized default fonts), `build.py` and `MagoLoader.spec` (`--collect-all=imageio_ffmpeg`).
- **Release:** bump `magoloader/version.py` and add a `CHANGELOG.md` entry.
- **Tests:** new `tests/test_branding.py` (HEX validation, overlay geometry, settings round trip, end-to-end FFmpeg run on a generated clip).
