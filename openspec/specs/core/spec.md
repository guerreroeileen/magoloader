# Core Specification

## Purpose
The Core module (`magoloader/core`) handles data models, profile/video extraction via `yt-dlp`, video downloading, application update checking, and telemetry/analytics.

## Requirements

### Requirement: Profile Metadata Extraction
The core system SHALL extract profile information and video entries from a given TikTok handle.

#### Scenario: Successful profile extraction
- **WHEN** a valid TikTok username is provided to `TikTokExtractor.extract`
- **THEN** it returns a `ProfileInfo` dataclass populated with uploader handle, thumbnail URL, and a list of `VideoEntry` objects without blocking the main UI thread.

#### Scenario: Failed extraction retry mechanism
- **WHEN** profile extraction encounters temporary network errors
- **THEN** `TikTokExtractor` retries extraction up to 3 times before raising an exception.

### Requirement: Video Downloading
The downloader module SHALL retrieve single or batch TikTok video files using `yt-dlp`.

#### Scenario: Download video with safe filename template
- **WHEN** `download_video` is called with a video URL and target directory
- **THEN** the video file is downloaded using the default template `%(upload_date)s_%(title).100s.%(ext)s` with filename restrictions enabled.

### Requirement: Automated Update Checking
The updater system SHALL check for application updates on GitHub Releases.

#### Scenario: Version check against GitHub API
- **WHEN** `GithubReleaseUpdater.check_for_updates` is invoked
- **THEN** it compares the current application version against the latest release tag and returns update status details.

### Requirement: Anonymous Usage Analytics
The telemetry module SHALL send anonymous event metrics to GA4.

#### Scenario: Telemetry event dispatching
- **WHEN** an event (e.g. app launch, profile search, download completed) is triggered
- **THEN** `GA4Tracker` dispatches the metric asynchronously using a persistent client ID.
