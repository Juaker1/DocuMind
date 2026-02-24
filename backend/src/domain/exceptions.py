"""
Excepciones del dominio de DocuMind.

Las capas de aplicación lanzan estas excepciones.
La capa API (FastAPI) las intercepta y las traduce a HTTPException.
"""


class DomainException(Exception):
    """Base de todas las excepciones de dominio."""


class InvalidCredentialsError(DomainException):
    """Credenciales de login incorrectas."""

    def __init__(self):
        super().__init__("Email o contraseña incorrectos")


class EmailAlreadyRegisteredError(DomainException):
    """Intento de registrar un email que ya existe."""

    def __init__(self, email: str):
        super().__init__(f"El email '{email}' ya está registrado")


class UserNotFoundError(DomainException):
    """No se encontró el usuario solicitado."""

    def __init__(self):
        super().__init__("Usuario no encontrado")


class DocumentNotFoundError(DomainException):
    """No se encontró el documento solicitado."""

    def __init__(self, document_id: int):
        super().__init__(f"Documento con ID {document_id} no encontrado")


class AccessDeniedError(DomainException):
    """El usuario no tiene permiso sobre el recurso."""

    def __init__(self):
        super().__init__("Acceso denegado")
