# -*- coding: utf-8 -*-
"""Módulo para seguimiento de analíticas con Google Analytics 4 (Measurement Protocol)."""

import json
import os
import threading
import uuid
import urllib.request
from typing import Dict, Any

from magoloader.constants import GA_MEASUREMENT_ID, GA_API_SECRET
from magoloader.version import __version__

# Directorio de configuración para guardar el client_id
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".magoloader")


class Analytics:
    _instance = None
    _client_id = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Analytics, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self._load_or_create_client_id()

    def _load_or_create_client_id(self):
        """Carga el ID del cliente o crea uno nuevo si no existe."""
        cid_file = os.path.join(CONFIG_DIR, "client_id")
        try:
            if not os.path.exists(CONFIG_DIR):
                os.makedirs(CONFIG_DIR, exist_ok=True)

            if os.path.exists(cid_file):
                with open(cid_file, "r") as f:
                    self._client_id = f.read().strip()
            
            if not self._client_id:
                raise ValueError("Client ID vacío")
        except (IOError, ValueError):
            self._client_id = str(uuid.uuid4())
            try:
                with open(cid_file, "w") as f:
                    f.write(self._client_id)
            except Exception:
                pass

    def track_event(self, event_name: str, params: Dict[str, Any] = None):
        """Envía un evento a GA4 en un hilo separado."""
        # Si no hay credenciales configuradas, no hacemos nada
        if "G-XXXXXXXXXX" in GA_MEASUREMENT_ID or "XXXXXXXXXXXXXXXXXXXXXX" in GA_API_SECRET:
            return

        if params is None:
            params = {}

        def _send():
            url = f"https://www.google-analytics.com/mp/collect?measurement_id={GA_MEASUREMENT_ID}&api_secret={GA_API_SECRET}"
            payload = {
                "client_id": self._client_id,
                "events": [{
                    "name": event_name,
                    "params": params,
                }]
            }
            
            try:
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    url, 
                    data=data, 
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req) as response:
                    pass # Éxito silencioso
            except Exception:
                pass # Fallo silencioso

        threading.Thread(target=_send, daemon=True).start()

    def track_download(self, video_count: int):
        """Rastrea el evento de descarga."""
        self.track_event("download", {
            "video_count": video_count,
            "app_version": __version__
        })
