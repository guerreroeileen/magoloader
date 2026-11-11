# Proposal

## Why

Today MagoLoader only downloads videos by analyzing a whole TikTok profile. Users who just want **one specific video** (a link shared with them, or a video from a profile with hundreds of entries) must analyze the full profile and look for it in the grid, which is slow and awkward. A "download by URL" option covers this common case directly.

The current UI is one window built in a single 390-line `MagoLoaderApp` class, so adding a second flow requires splitting it into reusable pieces first. This also makes later flows (other platforms, playlists, batch URLs) cheaper to add.

## What Changes

- The main window gets **two tabs**:
  1. **Profile:** the existing flow, unchanged in behavior (username → analyze → paginated grid → select → download).
  2. **Video URL:** new. The user pastes a TikTok video link and clicks **Fetch**. A preview card shows the thumbnail, title and duration. Then **Download** saves the video to the save folder with a progress bar.
- **Modular UI:**
  - Each tab becomes its own self-contained frame.
  - Shared pieces are extracted once and reused by both tabs: background task runner with translated error handling, save-folder picker, progress/download footer, and video card.
  - The save folder is **shared** between tabs: changing it in one tab updates the other.
- **Core:**
  - New single-video metadata extraction for a TikTok URL (title, duration, thumbnail, uploader).
  - TikTok video URL validation, covering full `tiktok.com/@user/video/<id>` links and short `vm.`/`vt.tiktok.com` and `tiktok.com/t/` links.
  - Optional download progress reporting.
- **i18n:** every new label, button, placeholder, status and error message is added in **es, en and pt**. New text:
  - tab names ("Profile", "Video URL")
  - URL placeholder
  - "Fetch" / "Fetching..." button
  - "Download" / "Downloading..." button
  - empty-state hint
  - "Saved to …" confirmation
  - errors for empty URL, invalid URL, and a video that is unavailable or private
- **Analytics:** a new anonymous `url_download` event, same mechanism as the existing download event.

### Non-goals

- Downloading several URLs at once (batch/queue) or playlists.
- Platforms other than TikTok. The URL validator and extractor are structured to allow it later, but only TikTok is accepted now.
- Quality/format selection, audio-only download, or renaming the output file. The existing filename template is kept.
- Remembering the save folder between app restarts.
- Runtime language switching. Labels keep using the current language detected at startup, like the rest of the app.

### Performance and threading

- URL validation runs locally on the UI thread, with no network.
- Fetching metadata, loading the thumbnail and downloading always run in background threads. Results return through the existing UI update queue, so the window never freezes.
- Each tab tracks its own running state:
  - A profile download and a URL download may run at the same time.
  - Within a tab, Fetch and Download are disabled while an operation is in progress, so the same action can't run twice.

## Capabilities

### New Capabilities
*None.* The project organizes specs by module (`core`, `ui`, `i18n`, `build`), so the new behavior is added to existing capabilities.

### Modified Capabilities
- `ui`: adds requirements for the tabbed main window, the "Video URL" tab (fetch → preview → download), a save folder shared across tabs, and translated UI text in the new tab.
- `core`: adds requirements for TikTok video URL validation, single-video metadata extraction, and download progress reporting.

The `i18n` requirement "Complete Translations for Every Feature" already covers the new keys, so no i18n delta is needed.

## Impact

- **Affected code:**
  - `magoloader/ui/app.py`: becomes a thin shell that hosts the tabs.
  - New `magoloader/ui/tabs/` package with `profile_tab.py` and `url_tab.py`.
  - New shared UI helpers: `magoloader/ui/task_runner.py` and `magoloader/ui/components/save_folder_picker.py`.
  - Adjusted components:
    - `Header`: the app title moves to the window level.
    - `Sidebar`: uses the shared folder picker.
    - `Footer`: configurable button text.
    - `VideoCard`: optional non-selectable mode for the preview.
- **Core:**
  - `magoloader/core/extractors/base.py` and `tiktok.py`: new `extract_video`.
  - `magoloader/core/downloader.py`: optional progress callback, returns the saved file path.
  - `magoloader/utils.py`: TikTok URL validator.
  - `magoloader/core/analytics.py`: new event.
- **i18n:** `magoloader/i18n/translations.py` gets the new keys in es, en and pt. `scripts/check_i18n.py` must pass.
- **Tests:** new unit tests for URL validation (`tests/test_url_validation.py`).
- **Dependencies:** none new. Uses the existing `customtkinter` (`CTkTabview`) and `yt-dlp`.
- **User experience:**
  - The window now shows two tabs at the top.
  - The Profile tab looks and works as before. The only difference is that the app title sits above the tabs instead of inside the profile header.
