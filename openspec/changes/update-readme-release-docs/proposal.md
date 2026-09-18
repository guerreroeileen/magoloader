# Proposal

## Why

The project documentation (`README.md`) currently lists general requirements without detailing the exact version of the `yt-dlp[curl-cffi]` library (`2026.8.19`), nor does it outline the step-by-step process for compiling standalone binaries and creating new release versions for distribution. Updating `README.md` and adding release documentation ensures maintainers and users have clear guidance on building and releasing new versions of MagoLoader.

## What Changes

- Update `README.md` dependencies section to explicitly reference `yt-dlp[curl-cffi]>=2026.8.19` and browser impersonation requirements.
- Add a new "Crear una nueva versión (Release)" section to `README.md` providing step-by-step instructions for versioning, clean builds via `build.py`, PyInstaller binary generation, and GitHub Release deployment.
- Update `magoloader/version.py` or release documentation as necessary.

## Capabilities

### New Capabilities
*None*

### Modified Capabilities
- `build`: Document step-by-step versioning and release packaging process for single-file binaries.

## Impact

- **Affected Files**: `README.md`, `openspec/specs/build/spec.md`.
- **Documentation**: Developers and maintainers obtain clear step-by-step instructions for releasing MagoLoader executable builds.
