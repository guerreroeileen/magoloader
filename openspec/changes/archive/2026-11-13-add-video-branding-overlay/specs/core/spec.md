# Spec Delta - Core

## ADDED Requirements

### Requirement: Optional Branding After Download
Video downloads SHALL optionally apply the branding overlay to the downloaded file, and SHALL behave exactly as before when no branding is requested.

#### Scenario: Download without branding
- **WHEN** a video is downloaded with branding disabled or not provided
- **THEN** the file is downloaded exactly as before (same name template, same content) and no video processing step runs.

#### Scenario: Download with branding
- **WHEN** a video is downloaded with valid, enabled branding settings
- **THEN** the video is downloaded, then branded, and the returned path points to the branded file, which uses the same file name the unbranded download would have used.

#### Scenario: Combined progress
- **WHEN** a download with branding is started with a progress listener
- **THEN** the listener receives one increasing fraction from 0 to 1 that covers both the download and the branding step.

#### Scenario: Branding failure keeps the download
- **WHEN** the download succeeds but branding fails
- **THEN** the unbranded file stays in the save folder and the raised error identifies it as a branding failure (distinct from a download failure) and includes the saved file path.
