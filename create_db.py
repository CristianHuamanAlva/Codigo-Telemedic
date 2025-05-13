from app import app
from extensiones import db
from models import *

with app.app_context():
    db.create_all()
    print("Base de datos y tablas creadas exitosamente.")
