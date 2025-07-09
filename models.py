from flask_login import UserMixin
from extensiones import db
from sqlalchemy import Text  # ✅ Este es el import que faltaba

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    correo = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    # Relación con Respuesta
    respuestas = db.relationship('Respuesta', backref='usuario', lazy=True)

    def __repr__(self):
        return f'<Usuario {self.nombre}>'


class Respuesta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))  # opcional, si aún quieres guardarlo como texto
    opcion = db.Column(db.String(150))
    decision = db.Column(db.String(150))
    satisfaccion = db.Column(db.String(50))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    historial_chat = db.Column(Text)  # Nueva columna para guardar el chat completo (en JSON)



    def __repr__(self):
        return f'<Respuesta {self.id}>'

