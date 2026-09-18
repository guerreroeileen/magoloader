# UI Specification

## Purpose
The UI module (`magoloader/ui`) delivers a CustomTkinter desktop interface inspired by TikTok's dark aesthetic (#121212 background, #FE2C55 red accent).

## Requirements

### Requirement: Application Window and Dark Theme
The application UI SHALL provide a responsive window with TikTok dark styling.

#### Scenario: Launch main application window
- **WHEN** the application starts
- **THEN** it initializes a `customtkinter.CTk` window with minimum dimensions `900x600`, dark appearance mode, and dark background palette (`#121212`).

### Requirement: Username Input and Directory Header
The header component SHALL allow entering a TikTok username and selecting the save directory.

#### Scenario: User analyzes profile
- **WHEN** the user inputs `@username` and clicks "Analyze"
- **THEN** a background thread is spawned to fetch profile data while showing loading indicators in the UI.

#### Scenario: User changes download directory
- **WHEN** the user clicks "Browse..."
- **THEN** a native folder picker dialog opens and updates the target save directory path.

### Requirement: Profile Sidebar and Selection Controls
The sidebar component SHALL display profile details and selection action controls.

#### Scenario: Select or deselect all videos
- **WHEN** the user toggles "Select All"
- **THEN** all video card checkboxes in the current view update their state accordingly.

### Requirement: Paginated Video Card Grid
The video grid SHALL present video entries in paginated cards.

#### Scenario: Page navigation
- **WHEN** the user clicks "Next" or "Previous" in the pagination bar
- **THEN** the grid displays 12 video cards corresponding to the selected page index.

### Requirement: Asynchronous Image Thumbnail Loader
Thumbnails SHALL be fetched asynchronously without freezing the UI.

#### Scenario: Image caching and thumbnail display
- **WHEN** a video card becomes visible
- **THEN** `ThumbnailLoader` checks local disk cache (`~/.magoloader/cache/thumbnails`), downloads missing thumbnails on background threads, and updates card image UI elements safely.

### Requirement: Update Notification Dialog
The application SHALL prompt users when an update is available.

#### Scenario: Display update modal
- **WHEN** a new version is detected by the updater
- **THEN** `UpdateDialog` presents release notes and direct update links in a modal window.
