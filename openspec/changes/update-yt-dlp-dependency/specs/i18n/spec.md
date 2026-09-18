# Spec Delta - i18n

## MODIFIED Requirements

### Requirement: Translation Catalog and Fallback
The i18n system SHALL retrieve localized strings with fallback handling.

#### Scenario: Retrieve existing translation string
- **WHEN** `get_text(key, lang)` is called for a valid key
- **THEN** it returns the translation string in the requested language with dynamic interpolation applied.

#### Scenario: Missing key fallback
- **WHEN** `get_text(key, lang)` is requested for a missing key in a specific language
- **THEN** it falls back to English (`en`) translation or returns the raw key identifier.

#### Scenario: Localized error messages for yt-dlp update instructions
- **WHEN** extraction fails due to an outdated `yt-dlp` version or site change
- **THEN** `get_text("err_ytdlp_outdated", lang)` returns localized instructions advising how to update `yt-dlp` via terminal in `es`, `en`, and `pt`.
