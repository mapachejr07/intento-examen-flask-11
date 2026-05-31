from flask import Flask, request, redirect, url_for, session, flash, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os, requests, random

url = "https://rickandmortyapi.com/api/character"

####### PETICIÓN #########
def get_dats():
    respuesta = requests.get(url)
    datos = respuesta.json()

    return datos['results']
####### FIN PETICIÓN #########

####### N_RANDOM #########
def n_random():
    numero = []

    while len(numero) != 5:
        n = random.randint(0,17)

        if n not in numero:
            numero.append(n)
    return numero
####### FIN N_RANDOM #########
load_dotenv()
app = Flask(__name__)

####### CREDENCIALES #########
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')

app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
conexion = MySQL(app)
####### FIN CREDENCIALES #########

####### JWT #########
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.secret_key = os.environ.get('SECOND_KEY')
####### FIN JWT #########


####### RUTAS BÁSICAS #########
@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.errorhandler(404)
def manejar_404(error):
    return render_template('404.html'), 404
####### FIN RUTAS BÁSICAS #########

####### REGISTER #########
@app.route('/register', methods=['POST'])
def register():
    if session.get('token'):
        flash('Eso que estás intentando no es muy taki taki rumba')
        return redirect(url_for('do_dashboard'))
    try:
        cursor = conexion.connection.cursor()

        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Debes rellenar todos los campos')
            return redirect(url_for('do_register'))
        
        query1 = 'SELECT email FROM users WHERE email = %s'
        cursor.execute(query1,(email,))
        user = cursor.fetchone()

        if user:
            flash('Ese usuario ya está registrado, porfavor inicia sesión')
            return 'Usuario ya registrado'
        
        password_hash = generate_password_hash(password)
        print(' he hasheado la contraseña')
        if email == 'admin@admin.com':
            query2 = 'INSERT INTO users(email,password,rol) VALUES(%s,%s, "admin")'

        else:
            query2 = 'INSERT INTO users(email,password) VALUES(%s,%s)'

        cursor.execute(query2, (email,password_hash))
        conexion.connection.commit()

        query3 = 'SELECT * FROM users WHERE email = %s'
        cursor.execute(query3,(email, ))
        full_user = cursor.fetchone()

        token = create_access_token(identity=email)

        session['id'] = full_user['id']
        session['rol'] = full_user['rol']
        session['token'] = token

        if session['rol'] != 'admin':
            datos = get_dats()
            numero = n_random()

            query4 = 'INSERT INTO favorites(id_user, name, gender, image) VALUES(%s,%s,%s,%s)'

            for i in numero:
                cursor.execute(query4, (
                    full_user['id'],
                    datos[i]['name'],
                    datos[i]['gender'],
                    datos[i]['image']
                ))
            conexion.connection.commit()
            flash('Usuario creado correctamente')
            return redirect(url_for('do_dashboard'))

        flash('Usuario creado correctamente')
        return redirect(url_for('do_admin'))

    except Exception as e:
        print(e)
        return 'Algo ha fallado en el register'
    
    finally:
        if cursor:
            cursor.close()

@app.route('/register')
def do_register():
    if session.get('token'):
        flash('No puedes acceder a esta zona, ya tienes una cuenta')
        return redirect(url_for('do_dashboard'))
    
    return render_template('register.html')
####### FIN REGISTER #########

####### LOGIN #########
@app.route('/login', methods=['POST'])
def login():
    if session.get('token'):
        flash('Eso que estás intentando no es muy taki taki rumba')
        return redirect(url_for('do_dashboard'))
    try:
        cursor = conexion.connection.cursor()

        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Faltan datos, rellene todos los campos')
            return redirect(url_for('do_login'))
        
        query1 = 'SELECT password FROM users WHERE email = %s'
        cursor.execute(query1, (email,))
        contrasena = cursor.fetchone()

        if not contrasena:
            flash('Ese usuario no existe')
            return redirect('do_register')
        
        password_check = check_password_hash(contrasena['password'], password)

        if not password_check:
            flash('Los datos no coinciden, prueba de nuevo')
            return redirect('do_login')

        query3 = 'SELECT * FROM users WHERE email = %s'
        cursor.execute(query3,(email, ))
        full_user = cursor.fetchone()

        token = create_access_token(identity=email)

        session['id'] = full_user['id']
        session['rol'] = full_user['rol']
        session['token'] = token
        
        flash('Has iniciado sesión')
        return redirect(url_for('do_dashboard'))


    except Exception as e:
        print(e)
        return 'Algo ha fallado en el login'
    
    finally:
        if cursor:
            cursor.close()

@app.route('/login')
def do_login():
    if session.get('token'):
        flash('No puedes acceder a esta zona, ya tienes una cuenta')
        return redirect(url_for('do_dashboard'))
    return render_template('login.html')
####### FIN LOGIN #########

####### DASHBOARD #########
@app.route('/dashboard')
def do_dashboard():
    if not session.get('token'):
        flash('No puedes acceder a esta zona, no tienes una cuenta')
        return redirect(url_for('do_register'))
    try:
        cursor = conexion.connection.cursor()

        id_user = session['id']

        query1 = 'SELECT * FROM favorites WHERE id_user = %s LIMIT 5'
        cursor.execute(query1, (id_user,))
        favoritos = cursor.fetchall()

        return render_template('dashboard.html', datos = favoritos)

    except Exception as e:
        print(e)
        return 'Algo ha fallaod en el dashboard'
    
    finally:
        if cursor:
            cursor.close()

####### FIN DASHBOARD #########

####### LOGOUT #########
@app.route('/logout')
def do_logout():
    if not session:
        flash('Necesitas haber iniciado en una cuenta primero para cerrarla, inútil')
        return redirect(url_for('do_register'))
    session.clear()
    return redirect(url_for('do_register'))
####### FIN LOGOUT #########

####### ADMIN #########
@app.route('/admin')
def do_admin():
    if not session.get('token'):
        flash('No puedes acceder a esta zona, no tienes una cuenta')
        return redirect(url_for('do_register'))

    if session['rol'] != 'admin':
        flash('No tienes acceso a esta zona, chaval que haces')
        return redirect(url_for('do_dashboard'))
    
    return render_template('admin.html')
####### FIN ADMIN #########


if __name__ == '__main__':
    app.run(debug=True)