# Spec Delta - Core

## ADDED Requirements

### Requirement: TikTok Video URL Validation
The core system SHALL decide locally, without network access, whether a given text is a TikTok single-video link.

#### Scenario: Accepted link formats
- **WHEN** the input (after trimming surrounding whitespace) is an `http` or `https` URL of the form `tiktok.com/@<user>/video/<numeric id>` (with or without `www.` or `m.`, with or without query parameters), or a short link on `vm.tiktok.com/<code>`, `vt.tiktok.com/<code>`, or `tiktok.com/t/<code>`
- **THEN** it is accepted as a TikTok video URL.

#### Scenario: Missing scheme
- **WHEN** the input is a valid TikTok video link without `http://` or `https://`
- **THEN** it is accepted and normalized to an `https://` URL.

#### Scenario: Rejected inputs
- **WHEN** the input is empty, a TikTok profile link (`tiktok.com/@<user>`), a non-TikTok domain (including look-alike domains such as `tiktok.com.evil.net`), or text that is not a URL
- **THEN** it is rejected.

### Requirement: Single Video Metadata Extraction
The core system SHALL extract metadata for a single TikTok video from its URL.

#### Scenario: Successful single video extraction
- **WHEN** a valid TikTok video URL is provided
- **THEN** it returns the video's canonical URL, id, title, duration, thumbnail URL, and uploader, resolving short links to the full video, and the call runs outside the UI thread.

#### Scenario: Retry on temporary errors
- **WHEN** single video extraction encounters a temporary network error
- **THEN** it retries up to 3 times before raising an error, consistent with profile extraction.

#### Scenario: Unavailable video
- **WHEN** the video is private, deleted, or the URL does not resolve to a single video
- **THEN** extraction raises an error that the UI can map to a translated message.

### Requirement: Download Progress Reporting
Video downloads SHALL optionally report progress and return the saved file location, without changing existing download behavior.

#### Scenario: Progress callback
- **WHEN** a download is started with a progress listener
- **THEN** the listener receives the completed fraction between 0 and 1 as the download advances, and receives 1 when it completes.

#### Scenario: Saved file location
- **WHEN** a download completes
- **THEN** the full path of the saved file is returned to the caller.

#### Scenario: Backward compatible batch downloads
- **WHEN** a download is started without a progress listener (as in the Profile tab batch download)
- **THEN** it behaves as before, using the template `%(upload_date)s_%(title).100s.%(ext)s` with filename restrictions enabled.
