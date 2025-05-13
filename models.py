from flask_login import UserMixin
from extensiones import db

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    correo = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return f'<Usuario {self.nombre}>'

class Respuesta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))
    opcion = db.Column(db.String(150))
    emergencias = db.Column(db.String(150))
    sintomas = db.Column(db.String(150))
    prevencion = db.Column(db.String(150))
    cuidados = db.Column(db.String(150))
    decision = db.Column(db.String(150))


    def __repr__(self):
        return f'<Respuesta {self.id}>'


