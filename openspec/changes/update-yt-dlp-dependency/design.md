# Design

## Context

See `proposal.md` for motivation. In `magoloader`, profile extraction relies on `yt_dlp.YoutubeDL`. When TikTok updates site HTML/API signatures or TLS fingerprint requirements, older `yt-dlp` releases fail. Currently, raw exceptions propagate to the UI without clear diagnostic instructions on how to update `yt-dlp`.

## Goals / Non-Goals

**Goals:**
- Catch `yt_dlp.utils.DownloadError` / `yt_dlp.utils.ExtractorError` in `TikTokExtractor` and `downloader`.
- Add dedicated `i18n` translation keys for `yt-dlp` update instructions in Spanish (`es`), English (`en`), and Portuguese (`pt`).
- Display clear, user-friendly error dialogs/status messages in CustomTkinter when extraction fails due to `yt-dlp` outdatedness or site changes.
- Ensure dependency specification in `requirements.txt` targets the latest stable `yt-dlp[curl-cffi]`.

**Non-Goals:**
- Automatically running `pip install --upgrade yt-dlp` without user consent or terminal execution privileges.
- Writing a custom parser to replace `yt-dlp`.

## Decisions

1. **Catch specific `yt_dlp.utils.DownloadError` and inspect error strings**:
   - *Rationale*: `yt-dlp` includes error message hints such as "TikTok", "outdated", or "Unable to extract".
   - *Alternative Considered*: Catching generic `Exception` only, which loses specificity.
2. **Expose localized troubleshooting instructions in UI popups**:
   - *Rationale*: Users running the source code or Python environment need explicit terminal commands (`pip install -U yt-dlp[curl-cffi]`) to update their environment.
   - *Alternative Considered*: Showing only generic "Extraction failed", which leaves users blocked without actionable resolution.

## Risks / Trade-offs

- **[Risk]**: `yt-dlp` error strings vary slightly across releases.
  - *Mitigation*: Fall back to a general extraction error message with `yt-dlp` update advice whenever `yt_dlp.utils.DownloadError` is raised.
