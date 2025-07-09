from flask import Flask, render_template, redirect, url_for, request, jsonify, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import Usuario, Respuesta
from extensiones import db, login_manager
from config import Config
import json



# Inicializar Flask
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Inicializar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@app.route('/guardar_respuesta', methods=['POST'])
def guardar_respuesta():
    data = request.get_json()
    nombre = data.get('nombre')
    opcion = data.get('opcion')
    decision = data.get('decision')
    historial = data.get('historial')  # 👈 nuevo campo recibido

    # Buscar el usuario por nombre (aunque lo ideal es usar el ID)
    usuario = Usuario.query.filter_by(nombre=nombre).first()

    if not usuario:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404

    nueva_respuesta = Respuesta(
        nombre=nombre,
        opcion=opcion,
        decision=decision,
        historial_chat=json.dumps(historial),  # 👈 convertimos el historial a JSON string
        usuario_id=usuario.id
    )

    db.session.add(nueva_respuesta)
    db.session.commit()

    print(f"Guardado: {nombre} - {opcion} - {decision}")

    return jsonify({"status": "ok"}), 200


@app.route('/guardar_satisfaccion', methods=['POST'])
def guardar_satisfaccion():
    data = request.get_json()
    nombre = data.get('nombre')
    satisfaccion = data.get('satisfaccion')

    # Buscar la última respuesta de ese usuario
    respuesta = Respuesta.query.filter_by(nombre=nombre).order_by(Respuesta.id.desc()).first()

    if respuesta:
        respuesta.satisfaccion = satisfaccion
        db.session.commit()
        print(f"Satisfacción guardada: {nombre} - {satisfaccion}")
        
        return jsonify({"status": "ok"}), 200
    else:
        return jsonify({"status": "error", "message": "Respuesta no encontrada"}), 404
    
@app.route('/historial_respuestas')
@login_required
def historial_respuestas():
    respuestas = Respuesta.query.filter_by(usuario_id=current_user.id).all()

    historial = []
    for i, r in enumerate(respuestas, start=1):
        historial.append({
            "id": r.id,  # 👈 Necesario para poder hacer fetch del historial completo
            "titulo": f"Consulta {i}",
            "opcion": r.opcion,
            "decision": r.decision,
            "satisfaccion": r.satisfaccion
        })

    return jsonify(historial)


# Ruta para el login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']
        
        # Verificación del correo
        if not correo or not password:
            flash('Por favor, ingrese su correo electrónico y contraseña', 'error')
            return redirect(url_for('login'))

        # Buscar el usuario
        user = Usuario.query.filter_by(correo=correo).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            print(f"Usuario autenticado: {current_user.nombre}, {current_user.correo}")
            return redirect(url_for('index'))
        else:
            flash('Correo o contraseña incorrectos. Por favor, intente de nuevo.', 'error')
    
    return render_template('login.html')


# Ruta para el registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        password = request.form['password']
        
        # Validaciones
        if not nombre or not correo or not password:
            flash('Por favor, complete todos los campos', 'error')
            return redirect(url_for('register'))
        
        # Validar si el correo ya existe
        existing_user = Usuario.query.filter_by(correo=correo).first()
        if existing_user:
            flash('Ya existe una cuenta con ese correo electrónico', 'error')
            return redirect(url_for('register'))
        
        # Validar longitud de la contraseña
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'error')
            return redirect(url_for('register'))
        
        # Crear el nuevo usuario
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = Usuario(nombre=nombre, correo=correo, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Cuenta creada exitosamente, por favor inicia sesión', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/obtener_historial/<int:respuesta_id>')
@login_required
def obtener_historial(respuesta_id):
    respuesta = Respuesta.query.filter_by(id=respuesta_id, usuario_id=current_user.id).first()

    if not respuesta:
        return jsonify({"error": "No encontrada"}), 404

    mensajes = []

    # Mensaje del usuario
    if respuesta.decision:
        mensajes.append({
            "emisor": "user",
            "contenido": respuesta.decision
        })

    # Mensaje del bot antes del video
    mensajes.append({
        "emisor": "bot",
        "contenido": f'Has seleccionado "{respuesta.decision}". Aquí está el video correspondiente.'
    })

    # Video como mensaje especial (puedes usar HTML del lado del cliente)
    mensajes.append({
        "emisor": "bot",
        "contenido": f"[VIDEO:{respuesta.decision}]"
    })

    # Satisfacción (si existe)
    if respuesta.satisfaccion:
        mensajes.append({
            "emisor": "bot",
            "contenido": f"Satisfacción: {respuesta.satisfaccion}"
        })

    return jsonify(mensajes)


# Ruta para el dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Ruta para logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Ruta para el index
@app.route('/')
def index():
    return render_template('index.html',user=current_user)


# Cargar el usuario por ID
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

if __name__ == '__main__':
    app.run(debug=True)
