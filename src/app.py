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
@app.route('/register')
def register():
    try:
        cursor = conexion.connection.cursor()

        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        


    except Exception as e:
        print(e)
        return 'Algo ha fallado en el register'
    
    finally:
        if cursor:
            cursor.close()

####### FIN REGISTER #########


if __name__ == '__main__':
    app.run(debug=True)