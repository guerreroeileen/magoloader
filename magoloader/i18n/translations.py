# -*- coding: utf-8 -*-
"""Cadenas traducidas (es, en, pt).

Toda clave nueva debe existir en los tres idiomas (ver scripts/check_i18n.py).
"""

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
            "   pip install -U \"yt-dlp[curl-cffi]\"\n\n"
            "2. El fallo a veces es intermitente; prueba de nuevo en unos minutos.\n\n"
            "3. Si sigue fallando, revisa en GitHub si hay una versión más reciente:\n"
            "   https://github.com/yt-dlp/yt-dlp/releases"
        ),
        "err_ytdlp_outdated": (
            "TikTok ha cambiado su web o yt-dlp está desactualizado.\n\n"
            "1. Actualiza yt-dlp desde la terminal:\n"
            "   pip install -U \"yt-dlp[curl-cffi]\"\n\n"
            "2. El fallo a veces es intermitente; prueba de nuevo en unos minutos.\n\n"
            "3. Si sigue fallando, revisa en GitHub si hay una versión más reciente:\n"
            "   https://github.com/yt-dlp/yt-dlp/releases"
        ),
        "error.ytdlp_ssl": (
            "Error SSL/TLS al conectar con TikTok (ej. TLSV1_ALERT_INTERNAL_ERROR).\n\n"
            "Instala el soporte de suplantación de navegador (recomendado):\n"
            "   pip install \"yt-dlp[curl-cffi]\"\n\n"
            "Or reinstala todas las dependencias:\n"
            "   pip install -r requirements.txt"
        ),
        "info.download_finished": "Descarga finalizada.",
        "video.no_title": "Sin título",
        "update.title": "Actualización disponible",
        "update.message": "Hay una nueva versión disponible ({latest}). Tu versión actual es {current}. Debes actualizar para continuar.",
        "update.download": "Descargar",
        "update.exit": "Salir",
        "tabs.profile": "Perfil",
        "tabs.url": "URL de video",
        "url.placeholder": "Pega el enlace del video de TikTok",
        "url.fetch": "Buscar",
        "url.fetching": "Buscando...",
        "url.empty_hint": "Pega un enlace de TikTok y pulsa Buscar para ver el video.",
        "url.download": "Descargar video",
        "url.downloading": "Descargando...",
        "url.saved_to": "Video guardado en:\n{path}",
        "error.no_url": "Escribe o pega la URL de un video de TikTok.",
        "error.invalid_url": "El enlace no es una URL válida de un video de TikTok.",
        "error.video_unavailable": "No se pudo obtener el video. Puede ser privado, haber sido eliminado o el enlace es incorrecto.",
        "branding.title": "PERSONALIZACIÓN DE VIDEO (Opcional)",
        "branding.enable": "Personalizar contenido",
        "branding.color": "Color del degradado (HEX)",
        "branding.pick_color": "Elegir color del degradado",
        "branding.logo": "Logo (imagen)",
        "branding.logo_dialog": "Seleccionar logo",
        "branding.image_files": "Imágenes",
        "branding.logo_remove": "Quitar",
        "branding.no_logo": "Sin logo",
        "branding.name": "Nombre de página (texto)",
        "branding.name_placeholder": "@MiPagina",
        "branding.applying": "Aplicando personalización...",
        "error.invalid_hex": "El color debe ser un código HEX válido, por ejemplo #0000FF.",
        "error.invalid_logo": "No se pudo abrir la imagen. Usa un archivo PNG, JPG o WEBP.",
        "info.saved_unbranded": (
            "El video se descargó, pero no se pudo aplicar la personalización. "
            "Se guardó sin personalizar en:\n{path}"
        ),
        "info.download_finished_unbranded": (
            "Descarga finalizada. {n} video(s) se guardaron sin personalizar "
            "porque no se pudo aplicar la personalización."
        ),
        "dialog.error_title": "Error",
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
            "   pip install -U \"yt-dlp[curl-cffi]\"\n\n"
            "2. The failure is sometimes intermittent; try again in a few minutes.\n\n"
            "3. If it still fails, check GitHub for a newer version:\n"
            "   https://github.com/yt-dlp/yt-dlp/releases"
        ),
        "err_ytdlp_outdated": (
            "TikTok has changed their site or yt-dlp is outdated.\n\n"
            "1. Update yt-dlp from the terminal:\n"
            "   pip install -U \"yt-dlp[curl-cffi]\"\n\n"
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
        "update.title": "Update Available",
        "update.message": "A new version is available ({latest}). Your current version is {current}. You must update to continue.",
        "update.download": "Download",
        "update.exit": "Exit",
        "tabs.profile": "Profile",
        "tabs.url": "Video URL",
        "url.placeholder": "Paste the TikTok video link",
        "url.fetch": "Fetch",
        "url.fetching": "Fetching...",
        "url.empty_hint": "Paste a TikTok link and press Fetch to preview the video.",
        "url.download": "Download video",
        "url.downloading": "Downloading...",
        "url.saved_to": "Video saved to:\n{path}",
        "error.no_url": "Enter or paste a TikTok video URL.",
        "error.invalid_url": "This link is not a valid TikTok video URL.",
        "error.video_unavailable": "Could not get the video. It may be private, deleted, or the link is wrong.",
        "branding.title": "VIDEO CUSTOMIZATION (Optional)",
        "branding.enable": "Personalize content",
        "branding.color": "Gradient color (HEX)",
        "branding.pick_color": "Choose gradient color",
        "branding.logo": "Logo (image)",
        "branding.logo_dialog": "Select logo",
        "branding.image_files": "Images",
        "branding.logo_remove": "Remove",
        "branding.no_logo": "No logo",
        "branding.name": "Page name (text)",
        "branding.name_placeholder": "@MyPage",
        "branding.applying": "Applying customization...",
        "error.invalid_hex": "The color must be a valid HEX code, for example #0000FF.",
        "error.invalid_logo": "Could not open the image. Use a PNG, JPG or WEBP file.",
        "info.saved_unbranded": (
            "The video was downloaded, but the customization could not be applied. "
            "It was saved without customization to:\n{path}"
        ),
        "info.download_finished_unbranded": (
            "Download finished. {n} video(s) were saved without customization "
            "because it could not be applied."
        ),
        "dialog.error_title": "Error",
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
            "   pip install -U \"yt-dlp[curl-cffi]\"\n\n"
            "2. O falho às vezes é intermitente; tenta novamente em alguns minutos.\n\n"
            "3. Se continuar a falhar, verifica no GitHub se há uma versão mais recente:\n"
            "   https://github.com/yt-dlp/yt-dlp/releases"
        ),
        "err_ytdlp_outdated": (
            "O TikTok alterou o site ou o yt-dlp está desatualizado.\n\n"
            "1. Atualiza o yt-dlp no terminal:\n"
            "   pip install -U \"yt-dlp[curl-cffi]\"\n\n"
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
        "update.title": "Atualização disponível",
        "update.message": "Uma nova versão está disponível ({latest}). Sua versão atual é {current}. Você deve atualizar para continuar.",
        "update.download": "Baixar",
        "update.exit": "Sair",
        "tabs.profile": "Perfil",
        "tabs.url": "URL do vídeo",
        "url.placeholder": "Cole o link do vídeo do TikTok",
        "url.fetch": "Buscar",
        "url.fetching": "Buscando...",
        "url.empty_hint": "Cole um link do TikTok e clique em Buscar para ver o vídeo.",
        "url.download": "Baixar vídeo",
        "url.downloading": "Baixando...",
        "url.saved_to": "Vídeo salvo em:\n{path}",
        "error.no_url": "Digite ou cole a URL de um vídeo do TikTok.",
        "error.invalid_url": "O link não é uma URL válida de vídeo do TikTok.",
        "error.video_unavailable": "Não foi possível obter o vídeo. Ele pode ser privado, ter sido excluído ou o link está incorreto.",
        "branding.title": "PERSONALIZAÇÃO DE VÍDEO (Opcional)",
        "branding.enable": "Personalizar conteúdo",
        "branding.color": "Cor do degradê (HEX)",
        "branding.pick_color": "Escolher cor do degradê",
        "branding.logo": "Logo (imagem)",
        "branding.logo_dialog": "Selecionar logo",
        "branding.image_files": "Imagens",
        "branding.logo_remove": "Remover",
        "branding.no_logo": "Sem logo",
        "branding.name": "Nome da página (texto)",
        "branding.name_placeholder": "@MinhaPagina",
        "branding.applying": "Aplicando personalização...",
        "error.invalid_hex": "A cor deve ser um código HEX válido, por exemplo #0000FF.",
        "error.invalid_logo": "Não foi possível abrir a imagem. Usa um ficheiro PNG, JPG ou WEBP.",
        "info.saved_unbranded": (
            "O vídeo foi descarregado, mas não foi possível aplicar a personalização. "
            "Foi guardado sem personalização em:\n{path}"
        ),
        "info.download_finished_unbranded": (
            "Descarregamento concluído. {n} vídeo(s) foram guardados sem personalização "
            "porque não foi possível aplicá-la."
        ),
        "dialog.error_title": "Erro",
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
