# Spec Delta - Core

## MODIFIED Requirements

### Requirement: Profile Metadata Extraction
The core system SHALL extract profile information and video entries from a given TikTok handle.

#### Scenario: Successful profile extraction
- **WHEN** a valid TikTok username is provided to `TikTokExtractor.extract`
- **THEN** it returns a `ProfileInfo` dataclass populated with uploader handle, thumbnail URL, and a list of `VideoEntry` objects without blocking the main UI thread.

#### Scenario: Failed extraction retry mechanism
- **WHEN** profile extraction encounters temporary network errors
- **THEN** `TikTokExtractor` retries extraction up to 3 times before raising an exception.

#### Scenario: Extraction failure due to site changes or outdated yt-dlp
- **WHEN** profile extraction fails due to TikTok site structure changes or an outdated `yt-dlp` library version
- **THEN** `TikTokExtractor` captures the `yt_dlp.utils.DownloadError` / `ExtractorError` and raises a descriptive `ExtractorError` containing diagnostic guidance for updating `yt-dlp`.
