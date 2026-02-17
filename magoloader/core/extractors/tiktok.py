# -*- coding: utf-8 -*-
import time
import yt_dlp
from typing import Optional, List
from .base import BaseExtractor
from ..models import ProfileInfo, VideoEntry

class TikTokExtractor(BaseExtractor):
    EXTRACT_RETRIES = 3
    RETRY_DELAY_SEC = 2
    
    def _base_opts(self) -> dict:
        opts = {
            "quiet": True,
            "no_warnings": True,
            # "impersonate": "chrome",  # Disabled to prevent assertion error crash
        }
        return opts

    def _first_thumbnail_url(self, *candidates) -> Optional[str]:
        for c in candidates:
            if isinstance(c, str) and c.startswith("http"):
                return c
            if isinstance(c, list) and c:
                first = c[0]
                url = first.get("url") if isinstance(first, dict) else first
                if isinstance(url, str) and url.startswith("http"):
                    return url
        return None

    def extract(self, username: str) -> ProfileInfo:
        url = f"https://www.tiktok.com/@{username.lstrip('@')}"
        opts = self._base_opts()
        opts.update({
            "extract_flat": True,
            "ignoreerrors": False,
        })
        
        last_error = None
        info = None
        
        for attempt in range(self.EXTRACT_RETRIES):
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                break
            except Exception as e:
                last_error = e
                if attempt < self.EXTRACT_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY_SEC)
        
        if info is None:
            if last_error:
                raise last_error
            raise RuntimeError("No se pudo extraer el perfil.")

        entries_raw = info.get("entries") or []
        entries_raw = [e for e in entries_raw if e and (e.get("url") or e.get("id"))]
        
        uploader = (
            info.get("uploader")
            or info.get("uploader_id")
            or info.get("channel")
            or username
        )
        thumb = self._first_thumbnail_url(
            info.get("thumbnail"),
            info.get("avatar"),
            info.get("thumbnails"),
        )

        entries: List[VideoEntry] = []
        for e in entries_raw:
            url_v = e.get("url")
            if not url_v and e.get("id"):
                url_v = f"https://www.tiktok.com/@{username.lstrip('@')}/video/{e.get('id')}"
            if not url_v:
                continue
                
            entry_thumb = self._first_thumbnail_url(
                e.get("thumbnail"),
                e.get("thumbnails"),
                e.get("cover"),
                e.get("dynamic_cover"),
            )
            entries.append(
                VideoEntry(
                    url=url_v,
                    id=e.get("id"),
                    title=e.get("title") or None,
                    duration=e.get("duration"),
                    thumbnail=entry_thumb,
                )
            )

        return ProfileInfo(
            uploader=uploader,
            username=username.lstrip("@"),
            thumbnail=thumb,
            entries=entries,
        )
