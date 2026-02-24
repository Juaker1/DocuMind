"""
Instancia compartida del rate limiter (slowapi).

Se define en un módulo propio para que tanto main.py (donde se registra
el handler 429 y se agrega al app.state) como las rutas (donde se aplican
los decoradores) puedan importarla sin dependencias circulares.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Clave por IP para endpoints públicos (login/register — usuario sin autenticar)
# En endpoints autenticados se puede usar el user_id del token como clave.
limiter = Limiter(key_func=get_remote_address)
