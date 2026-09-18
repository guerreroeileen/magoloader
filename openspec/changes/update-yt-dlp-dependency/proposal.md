# Proposal

## Why

When TikTok updates its site structure or security measures, older versions of `yt-dlp` can fail during profile extraction or video downloading, resulting in unhandled extractor errors or cryptic error messages. To maintain a smooth user experience, MagoLoader must ensure `yt-dlp` is up to date, provide clear actionable error messages in the UI when extraction fails due to site changes/outdated `yt-dlp`, and support updating `yt-dlp` dependencies smoothly.

## What Changes

- Update `requirements.txt` to require the latest stable `yt-dlp[curl-cffi]` package.
- Enhance error handling in `TikTokExtractor` and `downloader` to catch `yt_dlp.utils.DownloadError` / `ExtractorError`.
- Provide localized, actionable error messages in `i18n` notifying the user when TikTok extraction fails due to site changes or an outdated `yt-dlp` version.
- Display a helpful message guiding the user on how to update `yt-dlp` if needed.

## Capabilities

### New Capabilities
*None*

### Modified Capabilities
- `core`: Update profile extraction and video downloading error handling requirements to detect `yt-dlp` extractor errors and provide clear diagnostic context.
- `i18n`: Add localized translation keys for `yt-dlp` outdated/site change error guidance.

## Impact

- **Affected Code**: `requirements.txt`, `magoloader/core/extractors/tiktok.py`, `magoloader/core/downloader.py`, `magoloader/i18n/translations.py`, `magoloader/ui/app.py`.
- **Dependencies**: `yt-dlp[curl-cffi]` minimum version constraint updated.
- **User Experience**: Users encounter clear, translated error messages with instructions on how to resolve extraction errors caused by upstream TikTok site changes or outdated `yt-dlp`.
