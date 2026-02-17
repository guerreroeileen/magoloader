# -*- coding: utf-8 -*-
from .base import BaseExtractor
from .tiktok import TikTokExtractor

class ExtractorFactory:
    @staticmethod
    def get_extractor(url_or_username: str) -> BaseExtractor:
        # Simple logic: if it looks like a URL, parse domain. If just username, assume TikTok for now.
        # In the future, can detect platform by URL.
        return TikTokExtractor()
