# Internationalization (i18n) Specification

## Purpose
The i18n module (`magoloader/i18n`) provides multi-language support for MagoLoader across Spanish (`es`), English (`en`), and Portuguese (`pt`).

## Requirements

### Requirement: System Language Auto-Detection
The application SHALL automatically detect the user's operating system locale.

#### Scenario: Host locale matching
- **WHEN** the application initializes `detect_system_language()`
- **THEN** it inspects system locale settings and returns a supported language code (`es`, `en`, `pt`), defaulting to `en` if unsupported.

### Requirement: Translation Catalog and Fallback
The i18n system SHALL retrieve localized strings with fallback handling.

#### Scenario: Retrieve existing translation string
- **WHEN** `get_text(key, lang)` is called for a valid key
- **THEN** it returns the translation string in the requested language with dynamic interpolation applied.

#### Scenario: Missing key fallback
- **WHEN** `get_text(key, lang)` is requested for a missing key in a specific language
- **THEN** it falls back to English (`en`) translation or returns the raw key identifier.

### Requirement: Runtime Language Switching
The application UI SHALL allow runtime switching of interface text.

#### Scenario: User changes language dropdown
- **WHEN** the user selects a new language from the footer dropdown
- **THEN** UI labels, buttons, and status messages update their text immediately.
