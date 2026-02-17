# -*- coding: utf-8 -*-
"""Cadenas traducidas (es, en, pt)."""

from magoloader.i18n.detector import get_current_language

TRANSLATIONS = {
    "es": {
        "app.title": "MagoLoader - Descargador de videos sin marca de agua",
        "header.username_placeholder": "@usuario",
        "header.analyze": "Analizar",
        "header.analyzing": "Analizando...",
        "sidebar.profile": "Perfil",
        "sidebar.videos_available": "Videos disponibles: {count}",
        "sidebar.save_location": "Carpeta de guardado",
        "sidebar.browse": "Examinar...",
        "videos.select_page": "Seleccionar todos (página)",
        "videos.select_all": "Seleccionar todos los videos",
        "pagination.prev": "← Anterior",
        "pagination.next": "Siguiente →",
        "pagination.page": "Página {current} de {total}",
        "footer.download": "Descargar seleccionados ({n} videos)",
        "footer.progress": "Progreso: {pct}%",
        "error.no_username": "Escribe un @usuario de TikTok.",
        "error.no_videos_selected": "Selecciona al menos un video.",
        "error.profile_failed": "No se pudo obtener información del perfil.",
        "error.ytdlp": (
            "TikTok ha cambiado su web o yt-dlp está desactualizado.\n\n"
            "1. Actualiza yt-dlp desde la terminal:\n"
            "   pip install -U yt-dlp\n\n"
            "2. El fallo a veces es intermitente; prueba de nuevo en unos minutos.\n\n"
            "3. Si sigue fallando, revisa en GitHub si hay una versión más reciente:\n"
            "   https://github.com/yt-dlp/yt-dlp/releases"
        ),
        "error.ytdlp_ssl": (
            "Error SSL/TLS al conectar con TikTok (ej. TLSV1_ALERT_INTERNAL_ERROR).\n\n"
            "Instala el soporte de suplantación de navegador (recomendado):\n"
            "   pip install \"yt-dlp[curl-cffi]\"\n\n"
            "O reinstala todas las dependencias:\n"
            "   pip install -r requirements.txt"
        ),
        "info.download_finished": "Descarga finalizada.",
        "video.no_title": "Sin título",
    },
    "en": {
        "app.title": "MagoLoader - Video Downloader without watermark",
        "header.username_placeholder": "@username",
        "header.analyze": "Analyze",
        "header.analyzing": "Analyzing...",
        "sidebar.profile": "Profile",
        "sidebar.videos_available": "Videos available: {count}",
        "sidebar.save_location": "Save location",
        "sidebar.browse": "Browse...",
        "videos.select_page": "Select all (page)",
        "videos.select_all": "Select all videos",
        "pagination.prev": "← Previous",
        "pagination.next": "Next →",
        "pagination.page": "Page {current} of {total}",
        "footer.download": "Download selected ({n} videos)",
        "footer.progress": "Progress: {pct}%",
        "error.no_username": "Enter a TikTok @username.",
        "error.no_videos_selected": "Select at least one video.",
        "error.profile_failed": "Could not get profile information.",
        "error.ytdlp": (
            "TikTok has changed their site or yt-dlp is outdated.\n\n"
            "1. Update yt-dlp from the terminal:\n"
            "   pip install -U yt-dlp\n\n"
            "2. The failure is sometimes intermittent; try again in a few minutes.\n\n"
            "3. If it still fails, check GitHub for a newer version:\n"
            "   https://github.com/yt-dlp/yt-dlp/releases"
        ),
        "error.ytdlp_ssl": (
            "SSL/TLS error connecting to TikTok (e.g. TLSV1_ALERT_INTERNAL_ERROR).\n\n"
            "Install browser impersonation support (recommended):\n"
            "   pip install \"yt-dlp[curl-cffi]\"\n\n"
            "Or reinstall all dependencies:\n"
            "   pip install -r requirements.txt"
        ),
        "info.download_finished": "Download finished.",
        "video.no_title": "No title",
    },
    "pt": {
        "app.title": "MagoLoader - Baixar vídeos sem marca d'água",
        "header.username_placeholder": "@usuário",
        "header.analyze": "Analisar",
        "header.analyzing": "Analisando...",
        "sidebar.profile": "Perfil",
        "sidebar.videos_available": "Vídeos disponíveis: {count}",
        "sidebar.save_location": "Pasta de salvamento",
        "sidebar.browse": "Procurar...",
        "videos.select_page": "Selecionar todos (página)",
        "videos.select_all": "Selecionar todos os vídeos",
        "pagination.prev": "← Anterior",
        "pagination.next": "Próximo →",
        "pagination.page": "Página {current} de {total}",
        "footer.download": "Descarregar selecionados ({n} vídeos)",
        "footer.progress": "Progresso: {pct}%",
        "error.no_username": "Escreve um @usuário do TikTok.",
        "error.no_videos_selected": "Seleciona pelo menos um vídeo.",
        "error.profile_failed": "Não foi possível obter informações do perfil.",
        "error.ytdlp": (
            "O TikTok alterou o site ou o yt-dlp está desatualizado.\n\n"
            "1. Atualiza o yt-dlp no terminal:\n"
            "   pip install -U yt-dlp\n\n"
            "2. O falho às vezes é intermitente; tenta novamente em alguns minutos.\n\n"
            "3. Se continuar a falhar, verifica no GitHub se há uma versão mais recente:\n"
            "   https://github.com/yt-dlp/yt-dlp/releases"
        ),
        "error.ytdlp_ssl": (
            "Erro SSL/TLS ao ligar ao TikTok (ex.: TLSV1_ALERT_INTERNAL_ERROR).\n\n"
            "Instala o suporte de impersonação de navegador (recomendado):\n"
            "   pip install \"yt-dlp[curl-cffi]\"\n\n"
            "Ou reinstala as dependências:\n"
            "   pip install -r requirements.txt"
        ),
        "info.download_finished": "Descarregamento concluído.",
        "video.no_title": "Sem título",
    },
}


def t(key: str, **kwargs) -> str:
    """Devuelve la traducción del key en el idioma actual. kwargs para formato."""
    lang = get_current_language()
    strings = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    msg = strings.get(key, TRANSLATIONS["en"].get(key, key))
    if kwargs:
        try:
            return msg.format(**kwargs)
        except KeyError:
            return msg
    return msg
