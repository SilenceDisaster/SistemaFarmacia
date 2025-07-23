import sqlite3
import os
from datetime import datetime
import bcrypt # Importar bcrypt

DB_FILE = 'medicamentos.db'

def connect_db():
    """Establece una conexión con la base de datos SQLite."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row # Para acceder a las columnas por nombre
    return conn

# --- Funciones para crear tablas ---

def create_medicamentos_table():
    """Crea la tabla 'medicamentos' si no existe."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL UNIQUE, -- Código único del medicamento
            nombre TEXT NOT NULL,
            principio_activo TEXT NOT NULL,
            presentacion TEXT NOT NULL,
            stock_actual INTEGER NOT NULL DEFAULT 0,
            stock_minimo_alerta INTEGER NOT NULL DEFAULT 10,
            fecha_vencimiento TEXT NOT NULL, -- YYYY-MM-DD
            indicaciones TEXT,
            dosis_adultos TEXT,
            dosis_pediatricas TEXT,
            contraindicaciones TEXT,
            efectos_secundarios TEXT,
            interacciones TEXT,
            fabricante TEXT,
            ubicacion_farmacia TEXT,
            solo_emergencia INTEGER NOT NULL DEFAULT 0, -- 0=No, 1=Sí (Nuevo campo)
            ultima_actualizacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("Tabla 'medicamentos' verificada/creada.")

def create_users_table():
    """Crea la tabla 'usuarios' si no existe."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            usuario TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            rol TEXT NOT NULL, -- 'doctor', 'farmacia', 'admin', 'archivo'
            activo INTEGER NOT NULL DEFAULT 1,
            fecha_creacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("Tabla 'usuarios' verificada/creada.")

def create_patients_table():
    """Crea la tabla 'pacientes' si no existe."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_completo TEXT NOT NULL,
            cedula TEXT NOT NULL UNIQUE,
            codigo_expediente TEXT UNIQUE,
            fecha_nacimiento TEXT NOT NULL, -- YYYY-MM-DD
            telefono TEXT,
            direccion TEXT,
            barrio TEXT,
            condiciones_medicas TEXT -- Nuevo campo: Condiciones médicas, separadas por coma o JSON
        )
    ''')
    conn.commit()
    conn.close()
    print("Tabla 'pacientes' verificada/creada.")
    
def create_dispensations_table():
    """Crea la tabla 'dispensaciones' si no existe."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dispensaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_medicamento INTEGER NOT NULL,
            id_paciente INTEGER NOT NULL,
            id_doctor INTEGER NOT NULL, -- El usuario que registra la dispensación (rol doctor o farmacia)
            cantidad_dispensada INTEGER NOT NULL,
            fecha_dispensacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            motivo TEXT,
            notas_doctor TEXT,
            FOREIGN KEY (id_medicamento) REFERENCES medicamentos(id),
            FOREIGN KEY (id_paciente) REFERENCES pacientes(id),
            FOREIGN KEY (id_doctor) REFERENCES usuarios(id)
        )
    ''')
    conn.commit()
    conn.close()
    print("Tabla 'dispensaciones' verificada/creada.")

def create_appointments_table():
    """Crea la tabla 'citas' si no existe."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_paciente INTEGER NOT NULL,
            id_doctor INTEGER NOT NULL,
            fecha_cita TEXT NOT NULL, -- YYYY-MM-DD HH:MM
            motivo_cita TEXT,
            estado_cita TEXT NOT NULL DEFAULT 'programada', -- 'programada', 'completada', 'cancelada'
            FOREIGN KEY (id_paciente) REFERENCES pacientes(id),
            FOREIGN KEY (id_doctor) REFERENCES usuarios(id)
        )
    ''')
    conn.commit()
    conn.close()
    print("Tabla 'citas' verificada/creada.")

def create_dispensation_audit_log_table():
    """Crea la tabla 'dispensaciones_auditoria' para el registro de cambios."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dispensaciones_auditoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_dispensacion INTEGER NOT NULL,
            campo_modificado TEXT NOT NULL,
            valor_anterior TEXT,
            valor_nuevo TEXT,
            id_usuario_modifica INTEGER NOT NULL,
            nombre_usuario_modifica TEXT NOT NULL,
            fecha_modificacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_dispensacion) REFERENCES dispensaciones(id),
            FOREIGN KEY (id_usuario_modifica) REFERENCES usuarios(id)
        )
    ''')
    conn.commit()
    conn.close()
    print("Tabla 'dispensaciones_auditoria' verificada/creada.")


def create_all_tables():
    """Crea todas las tablas necesarias."""
    create_medicamentos_table()
    create_users_table()
    create_patients_table()
    create_dispensations_table()
    create_appointments_table() # Nueva tabla de citas
    create_dispensation_audit_log_table() # Nueva tabla de auditoría
    print(f"Base de datos '{DB_FILE}' y todas las tablas verificadas/creadas correctamente.")

# --- Funciones para añadir datos de ejemplo ---

def hash_password(password):
    """Genera un hash seguro para la contraseña."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def add_sample_users():
    """Añade algunos usuarios de ejemplo a la tabla de usuarios."""
    conn = connect_db()
    cursor = conn.cursor()

    users_to_add = [
        ("Dr. Juan Pérez", "jperez", hash_password("docpass123"), "doctor"),
        ("Lic. Ana Gómez", "agomez", hash_password("farmapass123"), "farmacia"),
        ("Admin Principal", "admin", hash_password("adminpass"), "admin"),
        ("Archivero Sofia", "ssofia", hash_password("arcpass123"), "archivo") # Nuevo usuario de archivo
    ]

    for nombre, usuario, pwd_hash, rol in users_to_add:
        try:
            cursor.execute('''
                INSERT INTO usuarios (nombre, usuario, password_hash, rol)
                VALUES (?, ?, ?, ?)
            ''', (nombre, usuario, pwd_hash, rol))
        except sqlite3.IntegrityError:
            print(f"Usuario '{usuario}' ya existe, omitiendo inserción de ejemplo.")
    conn.commit()
    conn.close()
    print("Usuarios de ejemplo añadidos (o verificados) correctamente.")

def add_sample_patients():
    """Añade algunos pacientes de ejemplo a la tabla de pacientes."""
    conn = connect_db()
    cursor = conn.cursor()

    patients_to_add = [
        # Añadido 'condiciones_medicas'
        ("María Fernanda López", "001-010180-0001X", "EXP001", "1980-01-01", "8888-1111", "Managua, Calle 1", "Barrio Central", "Diabetes Tipo 2, Hipertensión"),
        ("Carlos Alberto Ruiz", "002-050592-0002Y", "EXP002", "1992-05-05", "7777-2222", "Masaya, Avenida 2", "Barrio Modelo", "Asma"),
        ("Ana Gabriela Soto", "003-121275-0003Z", "EXP003", "1975-12-12", "5555-3333", "Granada, Calle Principal", "Barrio Histórico", "Problemas cardíacos"),
        ("Pedro Antonio Vargas", "004-030365-0004A", "EXP004", "1965-03-03", "9999-4444", "León, Callejon del Sol", "Barrio Viejo", "Diabetes Tipo 1")
    ]

    for nombre, cedula, cod_exp, fecha_nac, tel, dir, barrio, condiciones in patients_to_add: 
        try:
            cursor.execute('''
                INSERT INTO pacientes (nombre_completo, cedula, codigo_expediente, fecha_nacimiento, telefono, direccion, barrio, condiciones_medicas)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nombre, cedula, cod_exp, fecha_nac, tel, dir, barrio, condiciones)) 
        except sqlite3.IntegrityError:
            print(f"Paciente con cédula '{cedula}' o código de expediente '{cod_exp}' ya existe, omitiendo inserción de ejemplo.")
    conn.commit()
    conn.close()
    print("Pacientes de ejemplo añadidos (o verificados) correctamente.")

def add_sample_medicamentos():
    """Añade algunos datos de ejemplo a la tabla de medicamentos."""
    conn = connect_db()
    cursor = conn.cursor()

    sample_medicamentos = [
        # Añadido el campo 'solo_emergencia' (0=No, 1=Sí)
        ("01160216", "Paracetamol", "Paracetamol", "Tabletas 500mg", 150, 50, "2025-12-31",
         "Alivio del dolor y fiebre.", "500mg - 1000mg cada 4-6h", "10-15 mg/kg cada 4-6h",
         "Insuficiencia hepática grave.", "Náuseas, dolor abdominal.", "Alcohol, warfarina.",
         "Laboratorios X", "Estante A-1", 0), # No es solo emergencia

        ("01130920", "Amoxicilina", "Amoxicilina", "Cápsulas 500mg", 80, 20, "2026-06-30",
         "Infecciones bacterianas.", "250mg - 500mg cada 8h", "25-50 mg/kg/día dividido en dosis",
         "Alergia a penicilinas.", "Diarrea, náuseas, erupciones cutáneas.", "Metotrexato, probenecid.",
         "Farmacorp", "Estante B-2", 0), # No es solo emergencia

        ("01150105", "Ibuprofeno", "Ibuprofeno", "Tabletas 400mg", 45, 15, "2025-08-15",
         "Antiinflamatorio, analgésico, antipirético.", "200mg - 400mg cada 4-6h", "5-10 mg/kg cada 6-8h",
         "Úlcera péptica, asma, insuficiencia renal.", "Malestar estomacal, mareos.", "Anticoagulantes, diuréticos.",
         "MediFarma", "Estante A-2", 0), # No es solo emergencia

        ("01140310", "Omeprazol", "Omeprazol", "Cápsulas 20mg", 25, 10, "2024-09-01",
         "Úlcera gástrica, reflujo gastroesofágico.", "20mg una vez al día", "No recomendado en niños menores de 1 año.",
         "Hipersensibilidad.", "Dolor de cabeza, náuseas, diarrea.", "Clopidogrel, ketoconazol.",
         "GlobalPharma", "Estante C-1", 0), # No es solo emergencia
        
        ("01170425", "Adrenalina", "Epinefrina", "Inyectable 1mg/ml", 5, 2, "2024-10-01",
         "Reacciones alérgicas graves, paro cardíaco.", "Dosis según emergencia.", "Dosis según emergencia.",
         "No hay contraindicaciones absolutas en emergencia.", "Taquicardia, hipertensión.", "Betabloqueantes.",
         "Emergencia Pharma", "Refrigerador E-1", 1) # ¡Es solo emergencia!
    ]

    for med in sample_medicamentos:
        try:
            cursor.execute('''
                INSERT INTO medicamentos (
                    codigo, nombre, principio_activo, presentacion, stock_actual, stock_minimo_alerta,
                    fecha_vencimiento, indicaciones, dosis_adultos, dosis_pediatricas,
                    contraindicaciones, efectos_secundarios, interacciones, fabricante,
                    ubicacion_farmacia, solo_emergencia
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', med)
        except sqlite3.IntegrityError:
            print(f"'{med[1]}' (código: {med[0]}) ya existe en la base de datos, omitiendo inserción de ejemplo.")
    conn.commit()
    conn.close()
    print("Datos de ejemplo de medicamentos añadidos (o verificados) correctamente.")

def add_sample_dispensations():
    """Añade algunas dispensaciones de ejemplo."""
    conn = connect_db()
    cursor = conn.cursor()

    # Obtener IDs de ejemplo
    cursor.execute("SELECT id FROM medicamentos WHERE nombre = 'Paracetamol'")
    paracetamol_id = cursor.fetchone()['id']
    cursor.execute("SELECT id FROM medicamentos WHERE nombre = 'Amoxicilina'")
    amoxicilina_id = cursor.fetchone()['id']

    cursor.execute("SELECT id FROM pacientes WHERE nombre_completo = 'María Fernanda López'")
    maria_id = cursor.fetchone()['id']
    cursor.execute("SELECT id FROM pacientes WHERE nombre_completo = 'Carlos Alberto Ruiz'")
    carlos_id = cursor.fetchone()['id']

    cursor.execute("SELECT id FROM usuarios WHERE usuario = 'jperez'")
    jperez_id = cursor.fetchone()['id']
    cursor.execute("SELECT id FROM usuarios WHERE usuario = 'agomez'")
    agomez_id = cursor.fetchone()['id']

    sample_dispensations = [
        (paracetamol_id, maria_id, jperez_id, 20, "2024-06-15 10:30:00", "Dolor de cabeza, fiebre. Se le indicó reposo."),
        (amoxicilina_id, carlos_id, jperez_id, 14, "2024-07-01 14:00:00", "Infección de garganta. Reevaluar en 7 días."),
        (paracetamol_id, carlos_id, agomez_id, 10, "2024-07-10 09:00:00", "Control de fiebre post-vacuna.")
    ]

    for med_id, pac_id, doc_id, qty, fecha, notas in sample_dispensations:
        try:
            cursor.execute('''
                INSERT INTO dispensaciones (id_medicamento, id_paciente, id_doctor, cantidad_dispensada, motivo, notas_doctor)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (med_id, pac_id, doc_id, qty, fecha, notas))
            # Actualizar stock después de la dispensación de ejemplo
            # No es ideal llamar a update_medicine_stock_db aquí si ya se está insertando.
            # Asumimos que el stock inicial ya lo tiene en cuenta.
            # Para fines de ejemplo, si el stock se gestiona en la app, esta línea no es estrictamente necesaria aquí
            # porque la app se encarga de la lógica de stock.
            pass
        except sqlite3.IntegrityError:
            print(f"Dispensación de ejemplo ya existe o hay un error de integridad.")
        except Exception as e:
            print(f"Error al añadir dispensación de ejemplo: {e}")
    conn.commit()
    conn.close()
    print("Dispensaciones de ejemplo añadidas (o verificadas) correctamente.")

def add_sample_appointments():
    """Añade algunas citas de ejemplo."""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM pacientes WHERE nombre_completo = 'María Fernanda López'")
    maria_id = cursor.fetchone()['id']
    cursor.execute("SELECT id FROM pacientes WHERE nombre_completo = 'Carlos Alberto Ruiz'")
    carlos_id = cursor.fetchone()['id']

    cursor.execute("SELECT id FROM usuarios WHERE usuario = 'jperez'")
    jperez_id = cursor.fetchone()['id']
    cursor.execute("SELECT id FROM usuarios WHERE usuario = 'ssofia'") # Usar el ID del archivero para crear citas
    ssofia_id = cursor.fetchone()['id']


    sample_appointments = [
        (maria_id, jperez_id, "2024-08-01 09:00", "Revisión general", "programada"),
        (carlos_id, jperez_id, "2024-07-25 11:00", "Control de infección", "programada"),
        (maria_id, jperez_id, "2024-09-10 15:00", "Seguimiento diabetes", "programada")
    ]

    for pac_id, doc_id, fecha, motivo, estado in sample_appointments:
        try:
            # Asignar el id_doctor como el doctor de la cita, no el creador (que sería archivo)
            cursor.execute('''
                INSERT INTO citas (id_paciente, id_doctor, fecha_cita, motivo_cita, estado_cita)
                VALUES (?, ?, ?, ?, ?)
            ''', (pac_id, doc_id, fecha, motivo, estado))
        except sqlite3.IntegrityError:
            print(f"Cita de ejemplo ya existe o hay un error de integridad.")
    conn.commit()
    conn.close()
    print("Citas de ejemplo añadidas (o verificadas) correctamente.")


# --- Funciones de consulta (pueden ser útiles para depuración) ---
def get_all_medicamentos():
    """Recupera todos los medicamentos de la base de datos."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicamentos ORDER BY nombre ASC")
    medicamentos = cursor.fetchall()
    conn.close()
    return medicamentos

def get_all_users():
    """Recupera todos los usuarios de la base de datos."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, usuario, rol, activo FROM usuarios ORDER BY nombre ASC") # No mostrar password_hash
    users = cursor.fetchall()
    conn.close()
    return users

def get_all_patients():
    """Recupera todos los pacientes de la base de datos."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pacientes ORDER BY nombre_completo ASC")
    patients = cursor.fetchall()
    conn.close()
    return patients

def get_all_dispensations():
    """Recupera todas las dispensaciones de la base de datos."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dispensaciones ORDER BY fecha_dispensacion DESC")
    dispensations = cursor.fetchall()
    conn.close()
    return dispensations

def get_all_appointments():
    """Recupera todas las citas de la base de datos."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM citas ORDER BY fecha_cita DESC")
    appointments = cursor.fetchall()
    conn.close()
    return appointments

def get_all_dispensation_audit_logs():
    """Recupera todos los registros de auditoría de dispensaciones."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dispensaciones_auditoria ORDER BY fecha_modificacion DESC")
    logs = cursor.fetchall()
    conn.close()
    return logs


if __name__ == '__main__':
    create_all_tables()
    add_sample_users()
    add_sample_patients()
    add_sample_medicamentos()
    add_sample_dispensations() # Asegúrate de que los medicamentos, usuarios y pacientes existan antes de llamar a esta.
    add_sample_appointments() # Asegúrate de que los pacientes y doctores existan antes de llamar a esta.

    print("\n--- Estado de la Base de Datos ---")
    print("\nMedicamentos:")
    for med in get_all_medicamentos():
        print(f"- Código: {med['codigo']}, Nombre: {med['nombre']} ({med['presentacion']}): Stock {med['stock_actual']} (Venc: {med['fecha_vencimiento']}), Emergencia: {'Sí' if med['solo_emergencia'] else 'No'}")

    print("\nUsuarios:")
    for user in get_all_users():
        print(f"- ID: {user['id']}, Nombre: {user['nombre']}, Usuario: {user['usuario']}, Rol: {user['rol']}")

    print("\nPacientes:")
    for patient in get_all_patients():
        print(f"- ID: {patient['id']}, Nombre: {patient['nombre_completo']}, Cédula: {patient['cedula']}, Exp: {patient['codigo_expediente']}, Nacimiento: {patient['fecha_nacimiento']}, Barrio: {patient['barrio']}, Condiciones: {patient['condiciones_medicas']}")

    print("\nDispensaciones:")
    for disp in get_all_dispensations():
        print(f"- ID: {disp['id']}, Med ID: {disp['id_medicamento']}, Pac ID: {disp['id_paciente']}, Doc ID: {disp['id_doctor']}, Cant: {disp['cantidad_dispensada']}, Fecha: {disp['fecha_dispensacion']}, Notas: {disp['notas_doctor']}")

    print("\nCitas:")
    for appt in get_all_appointments():
        print(f"- ID: {appt['id']}, Pac ID: {appt['id_paciente']}, Doc ID: {appt['id_doctor']}, Fecha: {appt['fecha_cita']}, Motivo: {appt['motivo_cita']}, Estado: {appt['estado_cita']}")
    
    print("\nAuditoría de Dispensaciones:")
    for log in get_all_dispensation_audit_logs():
        print(f"- ID: {log['id']}, Disp ID: {log['id_dispensacion']}, Campo: {log['campo_modificado']}, Anterior: {log['valor_anterior']}, Nuevo: {log['valor_nuevo']}, Usuario: {log['nombre_usuario_modifica']}, Fecha: {log['fecha_modificacion']}")
