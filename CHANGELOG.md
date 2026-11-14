# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-11-13

### Added
- **Video customization (optional)**: new "Personalize content" panel in the Profile and Video URL tabs. When enabled, downloaded videos get a soft bottom gradient in a chosen HEX color, a logo in the top-right corner and a page/creator name centered over the gradient in white. Videos keep their original resolution and audio.
- Customization settings (color, logo, name and the checkbox) are remembered between sessions.
- If customization fails, the downloaded video is kept without customization and the user is told.

### Changed
- **Build**: FFmpeg is now bundled in the executable (via `imageio-ffmpeg`), which makes `MagoLoader.exe` larger.
- **Dependencies**: added `imageio-ffmpeg`; Pillow now requires 10.1 or newer.

## [1.1.0] - 2026-02-17

### Added
- **Google Analytics**: Integrated GA4 to track download usage anonymously.
- **Application Icon**: Added `magoloader.ico` as the application icon.
- **Versioning**: Added version display and management.

### Changed
- **UI/UX**: Redesigned video cards to be wider (340px) with larger, 16:9 thumbnails for better visibility.
- **Layout**: Adjusted the main grid to 2 columns to accommodate the wider cards.

## [1.0.0] - 2026-02-17

### Initial Release
- Basic functionality to download videos from TikTok (and other supported platforms via yt-dlp).
- Profile analysis and video listing.
- Batch download support.
