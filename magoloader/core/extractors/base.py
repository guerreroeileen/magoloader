# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from ..models import ProfileInfo

class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, url_or_username: str) -> ProfileInfo:
        """Extrae la información del perfil del username o URL proporcionada."""
        pass
