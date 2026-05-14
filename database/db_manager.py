import sqlite3
import os
import hashlib
import binascii

# Ajustar ruta de la DB relativa al punto de entrada
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'inventario.db')

def hash_password(password: str) -> str:
    """Hashear una contraseña usando PBKDF2-SHA256."""
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return binascii.hexlify(salt + key).decode('ascii')

def verify_password(password: str, hashed: str) -> bool:
    """Verificar una contraseña contra su hash PBKDF2-SHA256."""
    try:
        data = binascii.unhexlify(hashed.encode('ascii'))
        salt, key = data[:16], data[16:]
        new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return key == new_key
    except Exception:
        return False

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
            role TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT
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
             FOREIGN KEY (model_id) REFERENCES machine_models (id) ON DELETE SET NULL,
             FOREIGN KEY (distributor_id) REFERENCES distributors (id) ON DELETE SET NULL,
             FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE SET NULL
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
             completion_date TEXT,       -- Format YYYY-MM-DD, set when service is marked done
             applied_by TEXT,            -- username of who registered the service
             FOREIGN KEY (machine_id) REFERENCES machines (id) ON DELETE CASCADE
        )
    ''')

    # Índices para búsquedas en inventario
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_machines_status   ON machines(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_machines_model    ON machines(model_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_services_machine  ON services(machine_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_services_date     ON services(service_date)")

    # Usuario administrador por defecto
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password, role, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
            ('admin', hash_password('admin123'), 'admin', 'Administrador', 'Sistema')
        )

    # Proveedores autorizados (datos previos al uso del sistema)
    _distribuidores = [
        ("The Factory HKA",      ""),
        ("Corporación ECRS C.A", ""),
    ]
    for nombre, contacto in _distribuidores:
        cursor.execute(
            "INSERT OR IGNORE INTO distributors (name, contact) VALUES (?, ?)",
            (nombre, contacto)
        )

    conn.commit()
    conn.close()
    print("Estructura de base de datos sqlite inicializada correctamente.")

if __name__ == '__main__':
    # Modificar el DB_PATH a local si se corre directo desde el script
    DB_PATH = 'inventario.db'
    create_tables()
