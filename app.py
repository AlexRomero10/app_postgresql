from flask import Flask, render_template, abort
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import inspect
import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)

# Configura la conexión a PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql+psycopg2://practicabbdd:usuario@192.168.122.24/practicabbdd"

# Verifica que DATABASE_URL no esté vacío
if DATABASE_URL is None:
    raise ValueError("La variable de entorno DATABASE_URL no está definida.")

engine = create_engine(DATABASE_URL)

# Estilo común para todas las páginas
common_style = '''
    <style>
        body {
            background-color: #336699;
            color: white;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }
        h1 {
            text-align: center;
        }
        a {
            color: #FFD700;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid white;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #254e77;
        }
    </style>
'''

@app.route('/')
def index():
    return f'''
    <html>
        <head>
            {common_style}
            <style>
                img {{
                    display: block;
                    margin: 20px auto;
                    cursor: pointer;
                }}
            </style>
        </head>
        <body>
            <h1>Bienvenido a la aplicación Flask con PostgreSQL</h1>
            <a href="/tablas">
                <img src="https://www.postgresql.org/media/img/about/press/elephant.png" alt="PostgreSQL Logo" width="200">
            </a>
        </body>
    </html>
    '''

@app.route('/tablas')
def listar_tablas():
    try:
        inspector = inspect(engine)
        tablas = inspector.get_table_names()
        if not tablas:
            return f'''
            <html>
                <head>{common_style}</head>
                <body>
                    <h2>No se encontraron tablas en la base de datos.</h2>
                </body>
            </html>
            '''
        
        html = f'''
        <html>
            <head>
                {common_style}
            </head>
            <body>
                <h1>Tablas en la base de datos</h1>
                <ul>
        '''
        for tabla in tablas:
            html += f'<li><a href="/tabla/{tabla}">{tabla}</a></li>'
        
        html += '''
                </ul>
            </body>
        </html>
        '''
        return html
    except SQLAlchemyError as e:
        abort(500, description="Error al obtener tablas: " + str(e))

@app.route('/tabla/<nombre_tabla>')
def ver_tabla(nombre_tabla):
    try:
        inspector = inspect(engine)
        tablas = inspector.get_table_names()

        if nombre_tabla not in tablas:
            abort(404, description="Tabla no encontrada.")

        with engine.connect() as connection:
            query = text(f"SELECT * FROM {nombre_tabla};")
            result = connection.execute(query)
            
            columns = result.keys()
            registros = [dict(zip(columns, row)) for row in result]

        if not registros:
            return f'''
            <html>
                <head>{common_style}</head>
                <body>
                    <h1>No hay datos en la tabla {nombre_tabla}.</h1>
                    <a href="/tablas">Volver a la lista de tablas</a>
                </body>
            </html>
            '''

        registros_html = f'''
        <html>
            <head>{common_style}</head>
            <body>
                <h1>Datos de la Tabla: {nombre_tabla}</h1>
                <a href="/tablas">Volver a la lista de tablas</a>
                <table>
                    <tr>
        '''

        for key in columns:
            registros_html += f"<th>{key}</th>"
        registros_html += "</tr>"

        for registro in registros:
            registros_html += "<tr>"
            for key in columns:
                registros_html += f"<td>{registro.get(key, '')}</td>"
            registros_html += "</tr>"
        
        registros_html += '''
                </table>
            </body>
        </html>
        '''

        return registros_html
    except SQLAlchemyError as e:
        abort(500, description="Error al obtener registros: " + str(e))
    except Exception as e:
        abort(500, description="Error inesperado: " + str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
usuario@postgresql:~$ 
