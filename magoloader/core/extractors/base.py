# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from ..models import ProfileInfo, VideoEntry

class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, url_or_username: str) -> ProfileInfo:
        """Extrae la información del perfil del username o URL proporcionada."""
        pass

    @abstractmethod
    def extract_video(self, url: str) -> VideoEntry:
        """Extrae los metadatos de un único video a partir de su URL."""
        pass
