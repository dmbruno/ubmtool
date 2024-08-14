import os
from flask import Flask, jsonify, render_template, request, redirect, send_from_directory, url_for
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename


app = Flask(__name__)
mysql = MySQL(app)

# Configurar la conexión a MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'rootroot'
app.config['MYSQL_DB'] = 'pasaportes'

if os.environ.get('ENV') == 'production':
    UPLOADS = '/home/ubmviajes/pasaportesubm/ubmtool/src/uploads'
else:
    UPLOADS = os.path.join('src', 'uploads')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOADS'] = UPLOADS


@app.route('/fotodeusuario/<path:filename>')
def uploads(filename):
    return send_from_directory(os.path.join('UPLOADS'), filename)




@app.route('/')
def index():
    return render_template('clientes/index.html')

@app.route('/cliente/<int:id>')
def ver_cliente(id):
    cur = mysql.connection.cursor()
    sql = "SELECT * FROM clientes WHERE id = %s"
    cur.execute(sql, (id,))
    cliente = cur.fetchone()
    cur.close()
    return render_template('clientes/cliente.html', cliente=cliente)



@app.route('/clientes/', methods=['GET', 'POST'])
def clientes():
    cur = mysql.connection.cursor()
    
    if request.method == 'POST':
        apellido = request.form.get('apellido')
        nombre = request.form.get('nombre')
        
        if apellido:
            sql = "SELECT * FROM clientes WHERE apellido LIKE %s"
            cur.execute(sql, (f'%{apellido}%',))  # Usar %s y asegurarse de incluir el % en el valor
        elif nombre:
            sql = "SELECT * FROM clientes WHERE nombre LIKE %s"
            cur.execute(sql, (f'%{nombre}%',))  # Usar %s y asegurarse de incluir el % en el valor
        else:
            sql = "SELECT * FROM clientes"
            cur.execute(sql)
    else:
        sql = "SELECT * FROM clientes"
        cur.execute(sql)
    
    clientes = cur.fetchall()
    cur.close()
    return render_template('clientes/clientes.html', clientes=clientes)



@app.route('/create/')
def create():
    return render_template('clientes/create.html')



@app.route('/store', methods=['POST'])
def store():
    _nombre = request.form['txtnombre']
    _apellido = request.form['txtapellido']
    _fotoP = request.files['txtfotoP']
    _fotoV = request.files['txtfotoV']
    _fotoD = request.files['txtfotoD']

    print('este es el print', _fotoP, _fotoD, _fotoV)

    # Guardar las fotos en la carpeta src/uploads
    fotoP_filename = save_file(_fotoP)
    fotoV_filename = save_file(_fotoV)
    fotoD_filename = save_file(_fotoD)

    sql = "INSERT INTO clientes (nombre, apellido, fotopasaporte, fotovisa, fotodni) VALUES (%s, %s, %s, %s, %s);"
    datos = (_nombre, _apellido, fotoP_filename, fotoV_filename, fotoD_filename)

    cur = mysql.connection.cursor()
    cur.execute(sql, datos)
    mysql.connection.commit()
    cur.close()

    return redirect('/clientes')

def save_file(file):
    if file and file.filename:
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOADS'], filename)
        
        # Crear el directorio si no existe
        if not os.path.exists(app.config['UPLOADS']):
            os.makedirs(app.config['UPLOADS'])
        
        file.save(upload_path)
        return filename
    return None

@app.route('/search/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        apellido = request.form.get('apellido')
        cur = mysql.connection.cursor()
        sql = "SELECT * FROM clientes WHERE apellido = %s"
        cur.execute(sql, (apellido,))
        cliente = cur.fetchone()
        cur.close()
        if cliente:
            # Redirigir a la página de detalles del cliente
            return render_template('clientes/cliente.html', cliente=cliente)
        else:
            # Manejar el caso en que no se encuentra el cliente
            return render_template('clientes/search.html', error="Cliente no encontrado")
    return render_template('clientes/search.html')




@app.route('/eliminar_cliente/<int:id>', methods=['POST'])
def eliminar_cliente(id):
    cur = mysql.connection.cursor()
    sql_select = "SELECT fotopasaporte, fotovisa, fotodni FROM clientes WHERE id = %s;"
    cur.execute(sql_select, (id,))
    cliente = cur.fetchone()
    if cliente:
        fotopasaporte, fotovisa, fotodni = cliente

        sql_delete = "DELETE FROM clientes WHERE id = %s;"
        cur.execute(sql_delete, (id,))
        mysql.connection.commit()
        cur.close()

        delete_file(fotopasaporte)
        delete_file(fotovisa)
        delete_file(fotodni)

        return jsonify({'status': 'success'})
    else:
        cur.close()
        return jsonify({'status': 'error', 'message': 'Cliente no encontrado'}), 404

def delete_file(filename):
    if filename:
        filepath = os.path.join(app.config['UPLOADS'], filename)
        if os.path.exists(filepath):
            os.remove(filepath)

@app.route('/edit/<int:id>')
def edit(id):
    cur = mysql.connection.cursor()
    sql = "SELECT * FROM clientes WHERE id = %s;"
    cur.execute(sql, (id,))
    cliente = cur.fetchone()
    cur.close()
    return render_template('clientes/edit.html', cliente=cliente)

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    _nombre = request.form['txtnombre']
    _apellido = request.form['txtapellido']
    _fotoP = request.files['txtfotoP']
    _fotoV = request.files['txtfotoV']
    _fotoD = request.files['txtfotoD']

    cur = mysql.connection.cursor()
    sql = "UPDATE clientes SET nombre = %s, apellido = %s WHERE id = %s;"
    cur.execute(sql, (_nombre, _apellido, id))

    # Obtener los nombres de archivo actuales
    cur.execute("SELECT fotopasaporte, fotovisa, fotodni FROM clientes WHERE id = %s;", (id,))
    cliente = cur.fetchone()

    if cliente:
        fotopasaporte, fotovisa, fotodni = cliente

        # Eliminar los archivos antiguos si se van a reemplazar
        if _fotoP and _fotoP.filename:
            delete_file(fotopasaporte)
            fotoP_filename = save_file(_fotoP)
            cur.execute("UPDATE clientes SET fotopasaporte = %s WHERE id = %s;", (fotoP_filename, id))
        elif fotopasaporte:
            cur.execute("UPDATE clientes SET fotopasaporte = %s WHERE id = %s;", (fotopasaporte, id))

        if _fotoV and _fotoV.filename:
            delete_file(fotovisa)
            fotoV_filename = save_file(_fotoV)
            cur.execute("UPDATE clientes SET fotovisa = %s WHERE id = %s;", (fotoV_filename, id))
        elif fotovisa:
            cur.execute("UPDATE clientes SET fotovisa = %s WHERE id = %s;", (fotovisa, id))

        if _fotoD and _fotoD.filename:
            delete_file(fotodni)
            fotoD_filename = save_file(_fotoD)
            cur.execute("UPDATE clientes SET fotodni = %s WHERE id = %s;", (fotoD_filename, id))
        elif fotodni:
            cur.execute("UPDATE clientes SET fotodni = %s WHERE id = %s;", (fotodni, id))

    mysql.connection.commit()
    cur.close()
    return redirect('/clientes')





if __name__ == '__main__':
    app.run(debug=True)
