class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///usuarios.db'
    SECRET_KEY = 'mi_clave_secreta'
    SESSION_COOKIE_NAME = 'mi_cookie_sesion'  # Nombre de la cookie de sesión (opcional)
    PERMANENT_SESSION_LIFETIME = 3600  # Duración de la sesión (en segundos), por defecto es 31 días
    SESSION_PERMANENT = True
