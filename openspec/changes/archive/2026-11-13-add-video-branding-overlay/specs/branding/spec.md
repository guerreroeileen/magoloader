# Spec Delta - Branding

## Purpose

Lets users brand downloaded videos with their own gradient color, logo and page name as an overlay, without changing the video's size or other content.

## ADDED Requirements

### Requirement: Branding Settings
The system SHALL hold one set of branding settings made of an enabled flag, a gradient color, an optional logo image and an optional name text.

#### Scenario: Default settings
- **WHEN** no branding settings have ever been saved
- **THEN** branding is disabled, the color is `#0000FF`, there is no logo and the name is empty.

#### Scenario: Logo and name are optional
- **WHEN** branding is enabled with a valid color, no logo and an empty name
- **THEN** the settings are valid and only the gradient is applied.

### Requirement: HEX Color Validation
The system SHALL accept the gradient color only as a HEX code and normalize it.

#### Scenario: Accepted color formats
- **WHEN** the color text (after trimming whitespace) is `#RRGGBB`, `RRGGBB`, `#RGB` or `RGB` using hexadecimal digits in any letter case
- **THEN** it is accepted and normalized to uppercase `#RRGGBB` (for example `0af` becomes `#00AAFF`).

#### Scenario: Rejected color
- **WHEN** the color text is empty, has another length, or contains non-hexadecimal characters
- **THEN** it is rejected and, if branding is enabled, no download starts and a translated error asks for a valid HEX code.

### Requirement: Logo Validation
The system SHALL only accept a logo that can be opened as a PNG, JPG/JPEG or WEBP image.

#### Scenario: Valid logo chosen
- **WHEN** the user picks a readable PNG, JPG/JPEG or WEBP file
- **THEN** it becomes the branding logo, keeping its transparency.

#### Scenario: Invalid logo chosen
- **WHEN** the user picks a file that cannot be opened as an image
- **THEN** the previous logo is kept and a translated error is shown.

### Requirement: Branding Settings Persistence
The system SHALL remember the branding settings between application sessions.

#### Scenario: Settings restored on start
- **WHEN** the user changed the enabled flag, color, logo or name and later restarts the application
- **THEN** the panel shows the same values as before the restart.

#### Scenario: Logo kept after the original file moves
- **WHEN** the user picked a logo and later moves or deletes the original image file
- **THEN** the saved logo still works, because the application keeps its own copy.

#### Scenario: Missing or corrupt settings
- **WHEN** the saved settings file is missing, unreadable, or contains invalid values
- **THEN** the application starts with the default settings for the invalid values and does not crash.

### Requirement: Overlay Layout
The branding overlay SHALL be drawn at the exact resolution of the video, with element sizes relative to that resolution.

#### Scenario: Bottom gradient
- **WHEN** branding is applied with color C
- **THEN** a vertical gradient in color C covers the bottom part of the frame (about the lower 35%), fully transparent at its top edge and becoming almost opaque at the bottom edge with a smooth, eased transition, and the rest of the frame is unchanged.

#### Scenario: Logo position
- **WHEN** a logo is set
- **THEN** it is drawn in the top-right corner with padding from the top and right edges, scaled (keeping its aspect ratio) to fit a box proportional to the video size.

#### Scenario: Name position
- **WHEN** a name is set
- **THEN** it is drawn in white bold text, horizontally centered, near the bottom edge on top of the gradient, with a subtle shadow; if it is too wide for the frame minus side padding, the font size is reduced until it fits; if it still does not fit at the minimum font size, the end of the text is replaced with an ellipsis (`…`).

#### Scenario: Portrait and landscape videos
- **WHEN** branding is applied to a vertical (9:16) or horizontal (16:9) video
- **THEN** the gradient, logo and name keep the same relative positions and proportions in both.

### Requirement: Applying Branding to a Video
The system SHALL burn the overlay into a downloaded video without resizing it.

#### Scenario: Same size and audio
- **WHEN** branding is applied to a downloaded video
- **THEN** the result has the same width, height, frame rate and duration as the downloaded video, keeps the original audio unchanged, and replaces the downloaded file under the same file name.

#### Scenario: Video without audio
- **WHEN** the downloaded video has no audio track
- **THEN** branding still succeeds and the result has no audio track.

#### Scenario: Branding failure
- **WHEN** applying branding fails (for example the video cannot be read or the encoder fails)
- **THEN** the unbranded downloaded file is kept unchanged, no partial output file is left behind, and an error is raised that the UI can map to a translated message.

#### Scenario: Progress reporting
- **WHEN** branding is running with a progress listener
- **THEN** the listener receives the completed fraction between 0 and 1 as processing advances.

#### Scenario: No console window
- **WHEN** branding runs in the packaged Windows application
- **THEN** no console window appears.
