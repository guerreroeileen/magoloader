# Spec Delta - UI

## ADDED Requirements

### Requirement: Tabbed Main Window
The main window SHALL organize the download flows into tabs: a "Profile" tab containing the existing profile analysis and batch download flow, and a "Video URL" tab for downloading a single video by its link. Tab names SHALL be shown in the current application language.

#### Scenario: Application opens on the Profile tab
- **WHEN** the application window opens
- **THEN** it shows two tabs labeled with the translated names for "Profile" and "Video URL", the Profile tab is selected, and the application title is visible above the tabs.

#### Scenario: Switching tabs preserves state
- **WHEN** the user has analyzed a profile and selected videos in the Profile tab, switches to the Video URL tab, and switches back
- **THEN** the profile data, page, and video selection in the Profile tab are unchanged.

#### Scenario: Profile flow behavior is unchanged
- **WHEN** the user uses the Profile tab
- **THEN** username analysis, pagination of 12 videos per page, selection controls, folder selection, and batch download with progress behave exactly as before this change.

### Requirement: Download Video by URL
The "Video URL" tab SHALL let the user enter a TikTok video link, preview the video, and download it to the save folder.

#### Scenario: Preview a valid video link
- **WHEN** the user enters a valid TikTok video URL and clicks "Fetch" (or presses Enter)
- **THEN** the Fetch button is disabled and shows a "Fetching..." label while metadata loads in the background, and afterwards a preview card shows the video thumbnail, title (or the translated "Untitled" text), and duration, and the Download button becomes enabled.

#### Scenario: Download the previewed video
- **WHEN** a video preview is shown and the user clicks "Download"
- **THEN** the video downloads in the background to the current save folder using the standard filename format, the progress bar and percentage label update during the download, the Fetch and Download buttons are disabled until it finishes, and a translated confirmation including the saved file location is shown when it completes.

#### Scenario: Empty URL
- **WHEN** the user clicks "Fetch" with an empty URL field
- **THEN** a translated "enter a TikTok video URL" error is shown and no network request is made.

#### Scenario: Invalid or non-TikTok URL
- **WHEN** the user clicks "Fetch" with text that is not a TikTok video link (e.g. a profile link, another website, or random text)
- **THEN** a translated "not a valid TikTok video URL" error is shown and no network request is made.

#### Scenario: Video unavailable
- **WHEN** the link is a valid TikTok URL but the video is private, deleted, or cannot be extracted
- **THEN** the Fetch button is re-enabled, no preview is shown, and a translated error is displayed (the existing SSL and outdated yt-dlp guidance messages are used when those causes are detected).

#### Scenario: Changing the URL invalidates the preview
- **WHEN** a preview is shown and the user edits the URL field
- **THEN** the Download button is disabled until the new URL is fetched.

#### Scenario: Window stays responsive
- **WHEN** a fetch or download is in progress in the Video URL tab
- **THEN** the window remains responsive, the user can switch tabs, and the Profile tab can analyze and download independently.

### Requirement: Shared Save Folder Across Tabs
The application SHALL use a single save folder for all tabs.

#### Scenario: Change folder in one tab
- **WHEN** the user selects a new folder with "Browse..." in either tab
- **THEN** both tabs display the new folder and all subsequent downloads from either tab are saved there.

#### Scenario: Default folder
- **WHEN** the application starts
- **THEN** both tabs show the default folder `Downloads/MagoLoader` in the user's home directory.

### Requirement: Translated Video URL Tab
All visible text in the Video URL tab SHALL be available in every supported language (es, en, pt).

#### Scenario: Interface shown in the system language
- **WHEN** the application starts with Spanish, English, or Portuguese detected as the current language
- **THEN** every label, placeholder, button, hint, status, confirmation, and error message in the Video URL tab is displayed in that language.
