# -*- coding: utf-8 -*-
"""Version update checker via GitHub Releases API."""

import json
import urllib.request
import urllib.error
from collections import namedtuple

from packaging.version import parse as parse_version

from magoloader.version import __version__

# GitHub API endpoint for the latest release
_GITHUB_API_URL = (
    "https://api.github.com/repos/guerreroeileen/magoloader/releases/latest"
)

# Result type returned by check_for_updates()
UpdateInfo = namedtuple("UpdateInfo", ["update_available", "latest_version", "download_url"])


def check_for_updates() -> UpdateInfo:
    """Check whether a newer version is available on GitHub.

    Queries the GitHub Releases API for the latest release.  If the
    remote version is newer than the local ``__version__``, the
    returned ``UpdateInfo.update_available`` is ``True`` and
    ``download_url`` points to the release page.

    On any network or parsing error the function silently returns
    ``update_available=False`` so the application can still start
    when offline.
    """
    try:
        req = urllib.request.Request(
            _GITHUB_API_URL,
            headers={"Accept": "application/vnd.github+json", "User-Agent": "MagoLoader"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        tag = data.get("tag_name", "")
        # Strip leading 'v' if present (e.g. "v1.2.0" -> "1.2.0")
        latest_str = tag.lstrip("v")
        download_url = data.get("html_url", _GITHUB_API_URL)

        if not latest_str:
            return UpdateInfo(False, __version__, download_url)

        if parse_version(latest_str) > parse_version(__version__):
            return UpdateInfo(True, latest_str, download_url)

        return UpdateInfo(False, latest_str, download_url)

    except (urllib.error.URLError, json.JSONDecodeError, Exception):
        # Network unreachable, timeout, bad JSON, etc.  Allow the app
        # to start normally.
        return UpdateInfo(False, __version__, "")
