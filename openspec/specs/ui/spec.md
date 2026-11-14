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

### Requirement: Video Customization Panel
The Profile and Video URL tabs SHALL each show a "Video customization (optional)" panel in their side column, below the save location, bound to one shared set of branding settings.

#### Scenario: Panel collapsed when disabled
- **WHEN** "Personalize content" is unchecked
- **THEN** only the panel title and the checkbox are visible.

#### Scenario: Panel expanded
- **WHEN** the user checks "Personalize content"
- **THEN** the panel shows a HEX color field with a color swatch, a logo "Browse..." button with a logo preview and a "Remove" button, and a name text field.

#### Scenario: Pick color with the swatch
- **WHEN** the user clicks the color swatch
- **THEN** the native color picker opens with the current color, and the chosen color fills the HEX field and the swatch.

#### Scenario: Type a HEX color
- **WHEN** the user types a valid HEX code in the color field
- **THEN** the swatch shows that color; while the text is not a valid HEX code the swatch keeps the last valid color.

#### Scenario: Choose and remove a logo
- **WHEN** the user clicks "Browse...", picks an image, and later clicks "Remove"
- **THEN** a small preview of the logo appears after picking, and after removing, the preview shows a "No logo" placeholder.

#### Scenario: Shared between tabs
- **WHEN** the user changes any customization value in one tab
- **THEN** the panel in the other tab shows the same value.

#### Scenario: Fits at the minimum window size
- **WHEN** the window is at its minimum size of 900x600 and the panel is expanded
- **THEN** every side column control remains reachable (the side column scrolls if needed) and the video grid, pagination and footer stay visible.

#### Scenario: Locked during downloads
- **WHEN** a download is running in either tab
- **THEN** the customization controls are disabled in both tabs until all downloads finish.

### Requirement: Downloads With Customization
Downloads in both tabs SHALL use the customization settings in effect when the download starts.

#### Scenario: Customization disabled
- **WHEN** the user starts a download with "Personalize content" unchecked
- **THEN** the download works exactly as before.

#### Scenario: Invalid color blocks the download
- **WHEN** the user starts a download with "Personalize content" checked and an invalid HEX code
- **THEN** a translated error is shown and no download starts.

#### Scenario: Single video branding progress
- **WHEN** a branded download is running in the Video URL tab
- **THEN** the progress bar covers both steps and the button text changes to "Applying customization..." during the branding step.

#### Scenario: Single video branding failure
- **WHEN** branding fails in the Video URL tab after a successful download
- **THEN** a translated message says the video was saved without customization and shows the file path.

#### Scenario: Batch branding failures
- **WHEN** a batch download in the Profile tab finishes and branding failed for N videos (N > 0)
- **THEN** the final message says the download finished and that N videos were saved without customization.
