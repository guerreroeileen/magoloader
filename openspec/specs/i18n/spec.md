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

### Requirement: Complete Translations for Every Feature
Every user-facing string SHALL be translated into all supported languages (`es`, `en`, `pt`).

#### Scenario: New feature adds UI text
- **WHEN** a change adds or modifies a user-facing string
- **THEN** the string is accessed through `t(key)` and the key is added to the `es`, `en` and `pt` catalogs in `magoloader/i18n/translations.py` within the same change.

#### Scenario: Catalog consistency check
- **WHEN** `python scripts/check_i18n.py` runs
- **THEN** it passes only if every supported language has the same set of keys, no empty values, and matching `{placeholders}` for each key.

### Requirement: Runtime Language Switching
The application UI SHALL allow runtime switching of interface text.

#### Scenario: User changes language dropdown
- **WHEN** the user selects a new language from the footer dropdown
- **THEN** UI labels, buttons, and status messages update their text immediately.
