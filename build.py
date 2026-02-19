# -*- coding: utf-8 -*-
"""Script para construir el ejecutable de MagoLoader con PyInstaller."""

import os
import subprocess
import shutil
from magoloader.constants import WINDOW_TITLE

import sys

def build():
    # Limpiar builds anteriores
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")

    # Comando PyInstaller
    # --noconsole: Aplicación de ventana (sin consola)
    # --onefile: Un solo archivo .exe
    # --icon: Icono de la aplicación
    # --name: Nombre del ejecutable
    # --add-data: Incluir archivos no-python (el icono)
    # --collect-all: Recolectar dependencias completas de paquetes complejos (customtkinter, curl_cffi)
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--icon=magoloader.ico",
        f"--name={WINDOW_TITLE}",
        "--add-data=magoloader.ico;.",
        "--collect-all=customtkinter",
        "--collect-all=curl_cffi",  # Necesario para yt-dlp[curl-cffi]
        "main.py"
    ]
    
    print(f"Ejecutando: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    
    print("\nConstrucción finalizada. El ejecutable está en la carpeta 'dist'.")

if __name__ == "__main__":
    build()
