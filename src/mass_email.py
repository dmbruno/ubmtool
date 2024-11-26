import os
import pandas as pd
import re
import time
import threading  # Para usar hilos
import imghdr  # Para determinar el tipo de imagen
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, Response
from flask_mail import Message
from werkzeug.utils import secure_filename
from extensions import mail

# Crear el Blueprint
mass_email_bp = Blueprint('mass_email_bp', __name__)

# Directorio para guardar archivos subidos
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'xlsx'}

progress = 0  # Variable global para rastrear el progreso

# Funciones auxiliares
def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_email(email):
    """Valida una dirección de correo electrónico usando expresiones regulares."""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email)

def send_emails(app, file, subject, body, image_path):
    global progress
    with app.app_context():
        try:
            # Leer el archivo Excel
            df = pd.read_excel(file)
            
            # Normalizar los nombres de las columnas
            df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

            # Verificar que las columnas necesarias existen
            required_columns = {'correo', 'nombre', 'apellido'}
            if not required_columns.issubset(set(df.columns)):
                print("El archivo Excel debe contener las columnas 'correo', 'nombre' y 'apellido'.")
                return

            # Obtener los datos de correo, nombre y apellido
            emails_data = df[['correo', 'nombre', 'apellido']].dropna().drop_duplicates()

            total_emails = len(emails_data)
            progress = 0  # Inicializa el progreso

            for idx, row in emails_data.iterrows():
                email = row['correo']
                nombre = row['nombre']
                apellido = row['apellido']

                # Validar el correo electrónico
                if not validate_email(email):
                    print(f"Correo inválido: {email}")
                    continue

                try:
                    msg = Message(
                        subject=subject,
                        sender=app.config['MAIL_DEFAULT_SENDER'],
                        recipients=[email]
                    )

                    # Saludo personalizado
                    saludo_personalizado = f"Hola, {nombre} {apellido}! ¿Cómo estás?"

                    texto_generico = """
                    <p>Queremos compartir contigo nuestras últimas ofertas y promociones exclusivas. ¡No te pierdas esta oportunidad única!</p>
                    """

                    # Construir el contenido HTML del mensaje
                    msg_html = f'''
                        <h3>{saludo_personalizado}</h3>
                        {texto_generico}
                    '''

                    # Incluir el cuerpo adicional si existe
                   

                    # Incluir la imagen si existe
                    if image_path:
                        with open(image_path, 'rb') as img_file:
                            img_data = img_file.read()
                            img_name = os.path.basename(image_path)

                            # Determinar el tipo de imagen
                            img_type = imghdr.what(None, h=img_data)
                            if img_type is None:
                                print(f"El archivo de imagen '{img_name}' no es un formato de imagen válido.")
                                continue  # O manejar el error adecuadamente

                            # Mapear el tipo de imagen al tipo MIME
                            mime_type = f'image/{img_type}'

                            # Adjuntar la imagen al mensaje
                            msg.attach(
                                img_name,
                                mime_type,
                                img_data,
                                'inline',
                                headers={'Content-ID': '<imagen_cid>'}
                            )

                        # Añadir la imagen centrada al HTML
                        msg_html += f'''
                            <div style="text-align: center;">
                                <img src="cid:imagen_cid" alt="Imagen" style="max-width: 100%; height: auto;">
                            </div>
                        '''
                    else:
                        # Mensaje alternativo si no hay imagen
                        msg_html += '<p>¡Visita nuestro sitio web para más promociones!</p>'
                        
                    if body:
                        msg_html += f'''
                            <p>{body}</p>
                        '''
                    # Asignar el contenido HTML al mensaje
                    msg.html = msg_html

                    # Enviar el correo
                    mail.send(msg)
                    print(f"Correo enviado a {email}")
                except Exception as e:
                    print(f"Error al enviar correo a {email}: {e}")

                # Actualizar progreso
                progress = int(((idx + 1) / total_emails) * 100)
                print(f"Progreso actualizado a: {progress}%")  # Depuración

            progress = 100  # Marca como completo al terminar
            print("Envío de correos completado.")
        except Exception as e:
            print(f"Error al procesar el archivo: {e}")

# Ruta principal del Blueprint
@mass_email_bp.route('/mass_email', methods=['GET', 'POST'])
def mass_email():
    print(f"Request method: {request.method}")
    global progress
    if request.method == 'POST':
        # Obtener datos del formulario
        file = request.files.get('file')
        subject = request.form.get('subject')
        body = request.form.get('body')  # Ahora opcional
        image = request.files.get('image')

        # Validar archivo subido
        if not file or not allowed_file(file.filename):
            flash('Por favor, sube un archivo Excel válido (.xlsx)', 'danger')
            return redirect(request.url)

        # Crear la carpeta de uploads si no existe
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        # Guardar el archivo Excel
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Guardar la imagen (si existe)
        image_path = None
        if image and image.filename:
            image_filename = secure_filename(image.filename)
            image_path = os.path.join(UPLOAD_FOLDER, image_filename)
            image.save(image_path)

        # Inicializa progreso a 0
        progress = 0

        # Inicia un hilo para el envío de correos
        thread = threading.Thread(
            target=send_emails,
            args=(current_app._get_current_object(), filepath, subject, body, image_path)
        )
        thread.start()

        flash('El envío de correos ha comenzado. Puedes monitorear el progreso.', 'info')
        return redirect(request.url)

    return render_template('mass_email/mass_email.html')

@mass_email_bp.route('/mass_email/progress')
def email_progress():
    def generate():
        global progress
        while progress < 100:
            print(f"Progreso actual en backend: {progress}")  # Depuración
            time.sleep(0.1)  # Intervalo de actualización
            yield f"data:{progress}\n\n"
        progress = 0  # Reinicia el progreso al finalizar
    return Response(generate(), mimetype='text/event-stream')