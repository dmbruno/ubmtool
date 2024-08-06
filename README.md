# Pasaportes UBM - Viajes y Turismo

## Buscador de documentacion para agencia de viajes - UBM viajes y Turismo.
## la idea era unicamente traer de alguna forma las fotos de los documentos de los pasajeros
## para tenerlas a mano

## Pantalla de Inicio
<img src="./images/Captura de pantalla 2024-08-02 a las 4.59.11 p. m..png alt=" Descripción de la imagen width="150" height="200"/>

### Esta pantalla tiene la funcionalidad solicitada por el cliente,

    - Alta de Pasajero
    - Listado de pasajeros existentes
    - Buscar pasajeros

## clientes.HTML
<img src="./images/Captura de pantalla 2024-08-02 a las 4.59.49 p. m..png" alt="Descripción de la imagen" width="150" height="200"/>

    - Carga de los clientes existentes en la base de datos (MySQL)
    - Acciones de Editar y Eliminar clientes.


## Carga y Edicion de clientes

<img src="./images/Captura de pantalla 2024-08-02 a las 4.59.27 p. m..png" alt="Descripción de la imagen" width="150" height="200"/>

    - Alta de Nuevo Cliente/Pasajero
    - Edicion de algunos o todos los datos del cliente.    


## Manejo de arrores al buscar un apellido de un cliente inexistente en la base de datos

<img src="./images/Captura de pantalla 2024-08-02 a las 5.00.54 p. m..png" alt="Descripción de la imagen" width="150" height="200"/>

    - Simplemente condicione la aparicion o no del cartel al resultado del filtrado de la base de datos, si hay cliente o no.


## Resultado final 

<img src="./images/Captura de pantalla 2024-08-05 a las 8.08.07 p. m..png" alt="Descripción de la imagen" width="150" height="200"/>

    - La solicitud del cliente se remitia uicamente a tener a mano los documentos de los pasajeros al momento de necesitarlos, ya sea para chequear vencimientos, reserva de vuelos o bien check-in.




# Requerimientos/Dependecias:
    - blinker==1.8.2
    - cffi==1.16.0
    - click==8.1.7
    - cryptography==42.0.8
    - Flask==3.0.3
    - Flask-Cors==4.0.1
    - flask-marshmallow==1.2.1
    - Flask-MySQL==1.5.2
    - Flask-SQLAlchemy==3.1.1
    - itsdangerous==2.2.0
    - Jinja2==3.1.4
    - MarkupSafe==2.1.5
    - marshmallow==3.21.3
    - marshmallow-sqlalchemy==1.0.0
    - packaging==24.1
    - pycparser==2.22
    - PyMySQL==1.1.1
    - setuptools==70.2.0
    - SQLAlchemy==2.0.31
    - typing_extensions==4.12.2
    - Werkzeug==3.0.3
