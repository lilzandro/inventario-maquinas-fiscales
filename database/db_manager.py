import sqlite3
import os

# Ajustar ruta de la DB relativa al punto de entrada
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'inventario.db')

def get_connection():
    return sqlite3.connect(DB_PATH)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla Usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # Tabla Distribuidores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS distributors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT
        )
    ''')

    # Tabla Modelos de Máquinas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS machine_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model_name TEXT NOT NULL
        )
    ''')

    # Tabla Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            address TEXT,
            phone TEXT
        )
    ''')

    # Tabla Máquinas / Inventario
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS machines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            serial_number TEXT UNIQUE NOT NULL,
            model_id INTEGER,
            distributor_id INTEGER,
            status TEXT DEFAULT 'En Stock', -- 'En Stock', 'Instalada', 'Desincorporada'
            client_id INTEGER,
            FOREIGN KEY (model_id) REFERENCES machine_models (id),
            FOREIGN KEY (distributor_id) REFERENCES distributors (id),
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    ''')

    # Tabla Servicios (historial y próximos mantenimientos)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id INTEGER NOT NULL,
            service_type TEXT NOT NULL,
            service_date TEXT NOT NULL, -- Format YYYY-MM-DD
            next_maintenance_date TEXT, -- Format YYYY-MM-DD
            remarks TEXT,
            FOREIGN KEY (machine_id) REFERENCES machines (id)
        )
    ''')

    # Insertar usuario administrador por defecto si la base de datos es nueva
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        # Para simplificar propósitos iniciales se guarda en texto plano, aunque se recomienda usar hash
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")

    conn.commit()
    conn.close()
    print("Estructura de base de datos sqlite inicializada correctamente.")

if __name__ == '__main__':
    # Modificar el DB_PATH a local si se corre directo desde el script
    DB_PATH = 'inventario.db'
    create_tables()
