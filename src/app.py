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

app.config['UPLOADS'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')



ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}



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
    # Capturar los campos de texto
    _nombre = request.form.get('txtnombre')
    _apellido = request.form.get('txtapellido')
    _cuil = request.form.get('txtcuil')
    _numfrecuente1 = request.form.get('txtnumfrecuente1')  # Campos de números frecuentes
    _numfrecuente2 = request.form.get('txtnumfrecuente2')
    _numfrecuente3 = request.form.get('txtnumfrecuente3')

    # Capturar archivos
    _fotoP = request.files.get('txtfotoP')  # Foto de pasaporte argentino
    _fotoP2 = request.files.get('txtfotoP2')  # Foto de pasaporte europeo
    _fotoV = request.files.get('txtfotoV')   # Foto de visa
    _fotoD = request.files.get('txtfotoD')   # Foto de DNI

    # Guardar archivos y obtener nombres
    fotoP_filename = save_file(_fotoP) if _fotoP and _fotoP.filename else None
    fotoP2_filename = save_file(_fotoP2) if _fotoP2 and _fotoP2.filename else None
    fotoV_filename = save_file(_fotoV) if _fotoV and _fotoV.filename else None
    fotoD_filename = save_file(_fotoD) if _fotoD and _fotoD.filename else None

    # Insertar datos en la base de datos
    cur = mysql.connection.cursor()
    sql = """
        INSERT INTO clientes (nombre, apellido, cuil, numfrecuente1, numfrecuente2, numfrecuente3,
                              fotopasaporte, fotopasaporte2, fotovisa, fotodni)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    cur.execute(sql, (_nombre, _apellido, _cuil, _numfrecuente1, _numfrecuente2, _numfrecuente3,
                       fotoP_filename, fotoP2_filename, fotoV_filename, fotoD_filename))

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
    
    # Seleccionar archivos y datos relacionados con el cliente
    sql_select = "SELECT fotopasaporte, fotopasaporte2, fotovisa, fotodni FROM clientes WHERE id = %s;"
    cur.execute(sql_select, (id,))
    cliente = cur.fetchone()

    if cliente:
        fotopasaporte, fotopasaporte2, fotovisa, fotodni = cliente

        # Eliminar los registros del cliente en la base de datos
        sql_delete = "DELETE FROM clientes WHERE id = %s;"
        cur.execute(sql_delete, (id,))
        mysql.connection.commit()
        cur.close()

        # Eliminar archivos asociados al cliente
        delete_file(fotopasaporte)
        delete_file(fotopasaporte2)
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
    nombre = request.form['txtnombre']
    apellido = request.form['txtapellido']
    cuil = request.form['txtcuil']
    numfrecuente1 = request.form['txtnumfrecuente1']
    numfrecuente2 = request.form['txtnumfrecuente2']
    numfrecuente3 = request.form['txtnumfrecuente3']

    fotopasaporte = request.files.get('txtfotoP')
    fotopasaporte2 = request.files.get('txtfotoP2')
    fotovisa = request.files.get('txtfotoV')
    fotodni = request.files.get('txtfotoD')

    cur = mysql.connection.cursor()

    # Consulta para obtener la información actual del cliente
    cur.execute('SELECT fotopasaporte, fotopasaporte2, fotovisa, fotodni FROM clientes WHERE id = %s', (id,))
    existing_files = cur.fetchone()

    # Reemplazar los archivos solo si se han cargado nuevos
    fotopasaporte_path = fotopasaporte.filename if fotopasaporte else existing_files[0]
    fotopasaporte2_path = fotopasaporte2.filename if fotopasaporte2 else existing_files[1]
    fotovisa_path = fotovisa.filename if fotovisa else existing_files[2]
    fotodni_path = fotodni.filename if fotodni else existing_files[3]

    # Consulta para actualizar la información del cliente
    sql_update = """
    UPDATE clientes
    SET nombre = %s,
        apellido = %s,
        fotopasaporte = %s,
        fotopasaporte2 = %s,
        fotovisa = %s,
        fotodni = %s,
        cuil = %s,
        numfrecuente1 = %s,
        numfrecuente2 = %s,
        numfrecuente3 = %s
    WHERE id = %s;
    """

    # Actualizar los datos del cliente en la base de datos
    cur.execute(sql_update, (
        nombre,
        apellido,
        fotopasaporte_path,
        fotopasaporte2_path,
        fotovisa_path,
        fotodni_path,
        cuil,
        numfrecuente1,
        numfrecuente2,
        numfrecuente3,
        id
    ))

    mysql.connection.commit()

    # Guardar los archivos en el servidor solo si se han cargado nuevos
    if fotopasaporte:
        fotopasaporte.save(os.path.join(app.config['UPLOADS'], fotopasaporte.filename))
    if fotopasaporte2:
        fotopasaporte2.save(os.path.join(app.config['UPLOADS'], fotopasaporte2.filename))
    if fotovisa:
        fotovisa.save(os.path.join(app.config['UPLOADS'], fotovisa.filename))
    if fotodni:
        fotodni.save(os.path.join(app.config['UPLOADS'], fotodni.filename))

    cur.close()
    return redirect(url_for('clientes'))




if __name__ == '__main__':
    app.run(debug=True)

