import os
import pandas as pd
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_mail import Message
from werkzeug.utils import secure_filename
import re
from extensions import mail
from flask import Response
import time
import threading  # Para usar hilos
from flask import current_app







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

            # Validar direcciones de correo electrónico
            emails = df['correo'].dropna().unique()
            valid_emails = [email for email in emails if validate_email(email)]

            total_emails = len(valid_emails)
            progress = 0  # Inicializa el progreso

            for idx, email in enumerate(valid_emails, start=1):
                try:
                    msg = Message(
                        subject=subject,
                        sender=app.config['MAIL_DEFAULT_SENDER'],
                        recipients=[email]
                    )
                    msg.body = body
                    if image_path:
                        with open(image_path, "rb") as img_file:
                            msg.attach(
                                os.path.basename(image_path),
                                "image/png",
                                img_file.read()
                            )
                    mail.send(msg)
                    print(f"Correo enviado a {email}")
                except Exception as e:
                    print(f"Error al enviar correo a {email}: {e}")

                # Actualizar progreso
                progress = int((idx / total_emails) * 100)
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
        body = request.form.get('body')
        image = request.files.get('image')

        # Validar archivo subido
        if not file or not allowed_file(file.filename):
            flash('Por favor, sube un archivo Excel válido (.xlsx)', 'danger')
            return redirect(request.url)

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
            time.sleep(0.5)  # Intervalo de actualización
            yield f"data:{progress}\n\n"
        progress = 0  # Reinicia el progreso al finalizar
    return Response(generate(), mimetype='text/event-stream')
    

