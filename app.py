from flask import Flask, render_template, redirect, url_for, request, jsonify, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import Usuario, Respuesta
from extensiones import db, login_manager
from config import Config


# Inicializar Flask
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Inicializar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Ruta para recibir los datos del Webhook (requiere login)
@app.route('/webhook', methods=['POST'])  # Aquí volvemos a agregar el decorador
def webhook():
    

    data = request.get_json()

    # Imprimir los datos del Webhook para verificarlos en consola
    print("Datos recibidos del Webhook:")
    print(data)


    # Extraer las respuestas del JSON
    nombre = data.get('nombre')
    opcion = data.get('eleccion')
    emergencias = data.get('emergencias')
    sintomas = data.get('sintomas')
    prevencion = data.get('prevencion')
    cuidados = data.get('cuidados')
    decision = data.get('decision')

    # Guardar las respuestas del usuario
    respuesta = Respuesta(
        nombre=nombre,
        opcion=opcion,
        emergencias=emergencias,
        sintomas=sintomas,
        prevencion=prevencion,
        cuidados=cuidados,
        decision=decision,
    )

    db.session.add(respuesta)
    db.session.commit()

    return jsonify({'status': 'success'}), 200


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
