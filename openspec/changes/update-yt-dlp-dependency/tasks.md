# Tasks

## 1. i18n & Error Message Translations

- [x] 1.1 Add translation key `err_ytdlp_outdated` to `magoloader/i18n/translations.py` in `es`, `en`, and `pt` with actionable guidance on updating `yt-dlp[curl-cffi]`. Verify by inspecting dictionary entries.

## 2. Core Extractor & Downloader Error Handling

- [x] 2.1 Update `TikTokExtractor` in `magoloader/core/extractors/tiktok.py` to catch `yt_dlp.utils.DownloadError` and `yt_dlp.utils.ExtractorError`, wrapping them in user-friendly diagnostic messages. Verify by reviewing exception handling logic.
- [x] 2.2 Update `download_video` in `magoloader/core/downloader.py` to catch `DownloadError` and preserve descriptive error information. Verify error exception handling.

## 3. UI Error Presentation & Dependency Verification

- [x] 3.1 Update `magoloader/ui/app.py` profile extraction and download error handlers to present the localized `err_ytdlp_outdated` guidance when extraction errors occur. Verify UI popup/status updates.
- [x] 3.2 Ensure `requirements.txt` specifies `yt-dlp[curl-cffi]>=2026.8.19` and verify package loading.
