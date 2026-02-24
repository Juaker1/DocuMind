"""
Security Headers Middleware
Agrega cabeceras HTTP de seguridad a todas las respuestas de la API.

Qué hace cada cabecera:
  X-Content-Type-Options   → Desactiva MIME sniffing del navegador.
  X-Frame-Options          → Impide que la app sea embebida en un <iframe> (anti-clickjacking).
  X-XSS-Protection         → Activa el filtro XSS del navegador en modo bloqueo.
  Strict-Transport-Security→ Fuerza HTTPS por 1 año (solo en producción).
  Content-Security-Policy  → Restringe el origen de scripts, estilos e imágenes.
  Referrer-Policy          → Limita la información enviada en el header Referer.
  Permissions-Policy       → Desactiva APIs de browser que la API no necesita.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from src.config.settings import get_settings

settings = get_settings()

# CSP para API REST + consumida por Next.js frontend
# La API solo devuelve JSON, así que podemos ser muy restrictivos.
_CSP = (
    "default-src 'none'; "       # todo bloqueado por defecto
    "frame-ancestors 'none'"     # equivale a X-Frame-Options: DENY
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware que inyecta cabeceras de seguridad estándar en cada response.
    Se aplica a toda la API independientemente de la ruta.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response: Response = await call_next(request)

        # Desactiva MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Anti-clickjacking: prohíbe que la API sea cargada en un iframe
        response.headers["X-Frame-Options"] = "DENY"

        # Filtro XSS del navegador en modo bloqueo
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Limita la información enviada en el header Referer
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Desactiva APIs de browser que esta API no necesita
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), "
            "payment=(), usb=(), bluetooth=()"
        )

        # CSP restrictivo (API JSON pura, no sirve HTML/JS)
        response.headers["Content-Security-Policy"] = _CSP

        # HSTS — solo en producción (dev usa HTTP plano, HSTS lo rompería)
        if not settings.debug:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response
