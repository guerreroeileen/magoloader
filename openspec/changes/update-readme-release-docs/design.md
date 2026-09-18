# Design

## Context

See `proposal.md` for motivation. The project requires updated documentation for dependencies (`yt-dlp[curl-cffi]>=2026.8.19`) and step-by-step instructions for maintainers to release a new version of MagoLoader.

## Goals / Non-Goals

**Goals:**
- Update `README.md` to reference `yt-dlp[curl-cffi]>=2026.8.19`.
- Add a dedicated section to `README.md` detailing how to create and launch a new version release:
  1. Increment version in `magoloader/version.py`.
  2. Clean and build binary via `python build.py`.
  3. Test executable `dist/MagoLoader.exe`.
  4. Tag version in git (`git tag -a vX.Y.Z -m "Release vX.Y.Z"`).
  5. Publish GitHub Release with `dist/MagoLoader.exe`.

**Non-Goals:**
- Setting up automated GitHub Actions CI/CD pipelines in this change.

## Decisions

1. **Include release steps directly in `README.md`**:
   - *Rationale*: Keeps documentation centralized and accessible to anyone cloning or maintaining the repository.

## Risks / Trade-offs

- None identified.
