import streamlit as st
import sqlite3
import bcrypt
from datetime import datetime
import pandas as pd
import plotly.express as px

# Importar solo el tema oscuro desde styles.py
from styles import dark_theme_css

# --- Configuración de la Base de Datos ---
DB_FILE = 'medicamentos.db'

def connect_db():
    """Establece una conexión con la base de datos SQLite."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row # Para acceder a las columnas por nombre
    return conn

def hash_password(password):
    """Genera un hash seguro para la contraseña."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(hashed_password, user_password):
    """Verifica si la contraseña proporcionada coincide con el hash."""
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))

def authenticate_user(username, password):
    """
    Autentica un usuario contra la base de datos.
    Retorna el objeto de usuario si la autenticación es exitosa, de lo contrario None.
    """
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        if check_password(user['password_hash'], password):
            return user
    return None

# --- Funciones de Utilidad para la Base de Datos (CRUD) ---

# Medicamentos
def get_all_medicamentos_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicamentos ORDER BY nombre ASC")
    medicamentos = cursor.fetchall()
    conn.close()
    return [dict(row) for row in medicamentos]

def get_medicine_by_name_partial_db(search_term):
    """Busca medicamentos por nombre parcial."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicamentos WHERE nombre LIKE ? ORDER BY nombre ASC", (f'%{search_term}%',))
    medicamentos = cursor.fetchall()
    conn.close()
    return [dict(row) for row in medicamentos]

def get_medicine_by_id_db(medicine_id):
    """Obtiene un medicamento por su ID."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicamentos WHERE id = ?", (medicine_id,))
    medicine = cursor.fetchone()
    conn.close()
    return dict(medicine) if medicine else None

def add_medicine_db(codigo, nombre, principio_activo, presentacion, stock_actual, stock_minimo_alerta, fecha_vencimiento, indicaciones, dosis_adultos, dosis_pediatricas, contraindicaciones, efectos_secundarios, interacciones, fabricante, ubicacion_farmacia, solo_emergencia):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO medicamentos (codigo, nombre, principio_activo, presentacion, stock_actual, stock_minimo_alerta,
            fecha_vencimiento, indicaciones, dosis_adultos, dosis_pediatricas, contraindicaciones, efectos_secundarios,
            interacciones, fabricante, ubicacion_farmacia, solo_emergencia)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (codigo, nombre, principio_activo, presentacion, stock_actual, stock_minimo_alerta, fecha_vencimiento,
              indicaciones, dosis_adultos, dosis_pediatricas, contraindicaciones, efectos_secundarios,
              interacciones, fabricante, ubicacion_farmacia, solo_emergencia))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        st.error(f"Error: El código '{codigo}' o el nombre '{nombre}' ya existen.")
        return False
    finally:
        conn.close()

def update_medicine_db(id, codigo, nombre, principio_activo, presentacion, stock_actual, stock_minimo_alerta, fecha_vencimiento, indicaciones, dosis_adultos, dosis_pediatricas, contraindicaciones, efectos_secundarios, interacciones, fabricante, ubicacion_farmacia, solo_emergencia):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE medicamentos SET
            codigo = ?, nombre = ?, principio_activo = ?, presentacion = ?, stock_actual = ?,
            stock_minimo_alerta = ?, fecha_vencimiento = ?, indicaciones = ?, dosis_adultos = ?,
            dosis_pediatricas = ?, contraindicaciones = ?, efectos_secundarios = ?, interacciones = ?,
            fabricante = ?, ubicacion_farmacia = ?, solo_emergencia = ?, ultima_actualizacion = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (codigo, nombre, principio_activo, presentacion, stock_actual, stock_minimo_alerta, fecha_vencimiento,
              indicaciones, dosis_adultos, dosis_pediatricas, contraindicaciones, efectos_secundarios,
              interacciones, fabricante, ubicacion_farmacia, solo_emergencia, id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        st.error(f"Error: El código '{codigo}' o el nombre '{nombre}' ya existen para otro medicamento.")
        return False
    finally:
        conn.close()

def delete_medicine_db(id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM medicamentos WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def update_medicine_stock_db(medicine_id, quantity_change):
    """Actualiza el stock de un medicamento. quantity_change puede ser positivo (entrada) o negativo (salida)."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE medicamentos SET stock_actual = stock_actual + ?, ultima_actualizacion = CURRENT_TIMESTAMP WHERE id = ?", (quantity_change, medicine_id))
    conn.commit()
    conn.close()

# Usuarios
def get_all_users_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, usuario, rol, activo, fecha_creacion FROM usuarios ORDER BY nombre ASC")
    users = cursor.fetchall()
    conn.close()
    return [dict(row) for row in users]

def get_user_by_id_db(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, usuario, rol FROM usuarios WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_doctors_db():
    """Obtiene todos los usuarios con rol 'doctor'."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM usuarios WHERE rol = 'doctor' ORDER BY nombre ASC")
    doctors = cursor.fetchall()
    conn.close()
    return [dict(row) for row in doctors]

def add_user_db(nombre, usuario, password, rol):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        hashed_password = hash_password(password)
        cursor.execute("INSERT INTO usuarios (nombre, usuario, password_hash, rol) VALUES (?, ?, ?, ?)",
                       (nombre, usuario, hashed_password, rol))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        st.error(f"Error: El usuario '{usuario}' ya existe.")
        return False
    finally:
        conn.close()

def update_user_db(id, nombre, usuario, rol, activo):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE usuarios SET nombre = ?, usuario = ?, rol = ?, activo = ? WHERE id = ?",
                       (nombre, usuario, rol, activo, id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        st.error(f"Error: El nombre de usuario '{usuario}' ya está en uso.")
        return False
    finally:
        conn.close()

def reset_user_password_db(user_id, new_password):
    conn = connect_db()
    cursor = conn.cursor()
    hashed_password = hash_password(new_password)
    cursor.execute("UPDATE usuarios SET password_hash = ? WHERE id = ?", (hashed_password, user_id))
    conn.commit()
    conn.close()

def delete_user_db(id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (id,))
    conn.commit()
    conn.close()

# Pacientes
def get_all_patients_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pacientes ORDER BY nombre_completo ASC")
    patients = cursor.fetchall()
    conn.close()
    return [dict(row) for row in patients]

def get_patient_by_search_term_db(search_term):
    """Busca pacientes por nombre, cédula o código de expediente."""
    conn = connect_db()
    cursor = conn.cursor()
    search_term_like = f'%{search_term}%'
    cursor.execute('''
        SELECT * FROM pacientes
        WHERE nombre_completo LIKE ? OR cedula LIKE ? OR codigo_expediente LIKE ?
        ORDER BY nombre_completo ASC
    ''', (search_term_like, search_term_like, search_term_like))
    patients = cursor.fetchall()
    conn.close()
    return [dict(row) for row in patients]

def get_patient_by_id_db(patient_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pacientes WHERE id = ?", (patient_id,))
    patient = cursor.fetchone()
    conn.close()
    return dict(patient) if patient else None

def add_patient_db(nombre_completo, cedula, codigo_expediente, fecha_nacimiento, telefono, direccion, barrio, condiciones_medicas):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO pacientes (nombre_completo, cedula, codigo_expediente, fecha_nacimiento, telefono, direccion, barrio, condiciones_medicas)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nombre_completo, cedula, codigo_expediente, fecha_nacimiento, telefono, direccion, barrio, condiciones_medicas))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        st.error(f"Error: La cédula '{cedula}' o el código de expediente '{codigo_expediente}' ya existen para otro paciente.")
        return False
    finally:
        conn.close()

def update_patient_db(id, nombre_completo, cedula, codigo_expediente, fecha_nacimiento, telefono, direccion, barrio, condiciones_medicas):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE pacientes SET
            nombre_completo = ?, cedula = ?, codigo_expediente = ?, fecha_nacimiento = ?, telefono = ?, direccion = ?, barrio = ?, condiciones_medicas = ?
            WHERE id = ?
        ''', (nombre_completo, cedula, codigo_expediente, fecha_nacimiento, telefono, direccion, barrio, condiciones_medicas, id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        st.error(f"Error: La cédula '{cedula}' o el código de expediente '{codigo_expediente}' ya existen para otro paciente.")
        return False
    finally:
        conn.close()

def delete_patient_db(id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pacientes WHERE id = ?", (id,))
    conn.commit()
    conn.close()

# Dispensaciones
def get_all_dispensations_db():
    conn = connect_db()
    cursor = conn.cursor()
    # Unir tablas para obtener nombres en lugar de IDs
    cursor.execute('''
        SELECT d.id, m.nombre AS medicamento_nombre, m.codigo AS medicamento_codigo, m.presentacion AS medicamento_presentacion,
               p.nombre_completo AS paciente_nombre, p.cedula AS paciente_cedula, p.codigo_expediente AS paciente_expediente,
               u.nombre AS doctor_nombre, d.cantidad_dispensada, d.fecha_dispensacion, d.motivo, d.notas_doctor
        FROM dispensaciones d
        JOIN medicamentos m ON d.id_medicamento = m.id
        JOIN pacientes p ON d.id_paciente = p.id
        JOIN usuarios u ON d.id_doctor = u.id
        ORDER BY d.fecha_dispensacion DESC
    ''')
    dispensations = cursor.fetchall()
    conn.close()
    return [dict(row) for row in dispensations]

def get_dispensation_by_id_db(dispensation_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dispensaciones WHERE id = ?", (dispensation_id,))
    dispensation = cursor.fetchone()
    conn.close()
    return dict(dispensation) if dispensation else None


def get_dispensations_by_patient_id_db(patient_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT d.id, m.nombre AS medicamento_nombre, m.presentacion AS medicamento_presentacion,
               u.nombre AS doctor_nombre, d.cantidad_dispensada, d.fecha_dispensacion, d.motivo, d.notas_doctor
        FROM dispensaciones d
        JOIN medicamentos m ON d.id_medicamento = m.id
        JOIN usuarios u ON d.id_doctor = u.id
        WHERE d.id_paciente = ?
        ORDER BY d.fecha_dispensacion DESC
    ''', (patient_id,))
    dispensations = cursor.fetchall()
    conn.close()
    return [dict(row) for row in dispensations]

def add_dispensation_db(id_medicamento, id_paciente, id_doctor, cantidad_dispensada, motivo, notas_doctor):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        # Verificar stock antes de dispensar
        cursor.execute("SELECT stock_actual FROM medicamentos WHERE id = ?", (id_medicamento,))
        current_stock = cursor.fetchone()['stock_actual']
        if current_stock < cantidad_dispensada:
            st.error(f"Error: Stock insuficiente para el medicamento. Disponible: {current_stock}")
            return False

        cursor.execute('''
            INSERT INTO dispensaciones (id_medicamento, id_paciente, id_doctor, cantidad_dispensada, motivo, notas_doctor)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (id_medicamento, id_paciente, id_doctor, cantidad_dispensada, motivo, notas_doctor))
        conn.commit()
        # Actualizar stock del medicamento
        update_medicine_stock_db(id_medicamento, -cantidad_dispensada)
        return True
    except Exception as e:
        st.error(f"Error al registrar dispensación: {e}")
        return False
    finally:
        conn.close()

def update_dispensation_db(id, id_medicamento, id_paciente, id_doctor, cantidad_dispensada, motivo, notas_doctor, user_modifies_id, user_modifies_name):
    conn = connect_db()
    cursor = conn.cursor()
    
    # Obtener valores anteriores para auditoría
    old_dispensation = get_dispensation_by_id_db(id)
    
    try:
        # Verificar stock si la cantidad dispensada cambia
        # Primero, revertir el stock de la cantidad anterior si la cantidad cambia
        # Luego, aplicar el nuevo cambio. Esto es crucial para la precisión del inventario.
        cursor.execute("SELECT cantidad_dispensada FROM dispensaciones WHERE id = ?", (id,))
        old_cantidad = cursor.fetchone()['cantidad_dispensada']
        
        # Si la cantidad cambia, ajustamos el stock
        if old_cantidad != cantidad_dispensada:
            # Revertir la cantidad antigua al stock
            update_medicine_stock_db(id_medicamento, old_cantidad)
            
            # Verificar si el nuevo stock es suficiente antes de aplicar el cambio
            cursor.execute("SELECT stock_actual FROM medicamentos WHERE id = ?", (id_medicamento,))
            current_stock_after_revert = cursor.fetchone()['stock_actual']
            if current_stock_after_revert < cantidad_dispensada:
                st.error(f"Error: Stock insuficiente para la nueva cantidad. Disponible: {current_stock_after_revert}")
                # Si no hay suficiente stock, revertir el cambio de stock y salir
                update_medicine_stock_db(id_medicamento, -old_cantidad) # Poner el stock como estaba
                return False
            
            # Aplicar la nueva cantidad al stock
            update_medicine_stock_db(id_medicamento, -cantidad_dispensada)

        cursor.execute('''
            UPDATE dispensaciones SET
            id_medicamento = ?, id_paciente = ?, id_doctor = ?, cantidad_dispensada = ?, motivo = ?, notas_doctor = ?
            WHERE id = ?
        ''', (id_medicamento, id_paciente, id_doctor, cantidad_dispensada, motivo, notas_doctor, id))
        conn.commit()

        # Registrar cambios en la tabla de auditoría
        if old_dispensation:
            changes = []
            if old_dispensation['cantidad_dispensada'] != cantidad_dispensada:
                changes.append(('cantidad_dispensada', old_dispensation['cantidad_dispensada'], cantidad_dispensada))
            if old_dispensation['motivo'] != motivo:
                changes.append(('motivo', old_dispensation['motivo'], motivo))
            if old_dispensation['notas_doctor'] != notas_doctor:
                changes.append(('notas_doctor', old_dispensation['notas_doctor'], notas_doctor))
            # Podrías añadir más campos aquí si se permite su edición

            for field, old_val, new_val in changes:
                cursor.execute('''
                    INSERT INTO dispensaciones_auditoria (id_dispensacion, campo_modificado, valor_anterior, valor_nuevo, id_usuario_modifica, nombre_usuario_modifica)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (id, field, str(old_val), str(new_val), user_modifies_id, user_modifies_name))
            conn.commit()
        
        return True
    except Exception as e:
        st.error(f"Error al actualizar dispensación: {e}")
        conn.rollback() # Revertir cualquier cambio si hay un error
        return False
    finally:
        conn.close()

def get_all_dispensation_audit_logs_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT da.id, da.id_dispensacion, da.campo_modificado, da.valor_anterior, da.valor_nuevo,
               da.nombre_usuario_modifica, da.fecha_modificacion
        FROM dispensaciones_auditoria da
        ORDER BY da.fecha_modificacion DESC
    ''')
    logs = cursor.fetchall()
    conn.close()
    return [dict(row) for row in logs]


# Citas
def get_all_appointments_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.id, p.nombre_completo AS paciente_nombre, p.cedula AS paciente_cedula,
               u.nombre AS doctor_nombre, c.fecha_cita, c.motivo_cita, c.estado_cita, c.id_doctor
        FROM citas c
        JOIN pacientes p ON c.id_paciente = p.id
        JOIN usuarios u ON c.id_doctor = u.id
        ORDER BY c.fecha_cita DESC
    ''')
    appointments = cursor.fetchall()
    conn.close()
    return [dict(row) for row in appointments]

def get_appointment_by_id_db(appointment_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM citas WHERE id = ?", (appointment_id,))
    appointment = cursor.fetchone()
    conn.close()
    return dict(appointment) if appointment else None

def get_appointments_by_patient_id_db(patient_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.id, u.nombre AS doctor_nombre, c.fecha_cita, c.motivo_cita, c.estado_cita, c.id_doctor
        FROM citas c
        JOIN usuarios u ON c.id_doctor = u.id
        WHERE c.id_paciente = ?
        ORDER BY c.fecha_cita DESC
    ''', (patient_id,))
    appointments = cursor.fetchall()
    conn.close()
    return [dict(row) for row in appointments]

def add_appointment_db(id_paciente, id_doctor, fecha_cita, motivo_cita, estado_cita='programada'):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO citas (id_paciente, id_doctor, fecha_cita, motivo_cita, estado_cita)
            VALUES (?, ?, ?, ?, ?)
        ''', (id_paciente, id_doctor, fecha_cita, motivo_cita, estado_cita))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error al programar cita: {e}")
        return False
    finally:
        conn.close()

def update_appointment_db(id, id_paciente, id_doctor, fecha_cita, motivo_cita, estado_cita):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE citas SET
            id_paciente = ?, id_doctor = ?, fecha_cita = ?, motivo_cita = ?, estado_cita = ?
            WHERE id = ?
        ''', (id_paciente, id_doctor, fecha_cita, motivo_cita, estado_cita, id))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error al actualizar cita: {e}")
        return False
    finally:
        conn.close()

def delete_appointment_db(id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM citas WHERE id = ?", (id,))
    conn.commit()
    conn.close()


# --- Lógica de Autenticación Principal ---
def login():
    # Custom CSS for vertical alignment and card styling
    st.markdown("""
        <style>
            /* Ensures the entire app container can flex */
            .stApp {
                display: flex;
                flex-direction: column;
                min-height: 100vh;
            }
            /* Centers the main content block vertically */
            .main .block-container {
                flex-grow: 1;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                padding-top: 0rem; /* Remove default padding to allow full vertical control */
                padding-bottom: 0rem; /* Remove default padding */
            }
            /* Styling for the login card */
            .login-card {
                width: 90%; /* Adjust width for better responsiveness */
                max-width: 450px; /* Max width for larger screens */
                padding: 30px; /* Increased padding */
                border-radius: 12px; /* Slightly more rounded corners */
                background-color: #2e3b4e; /* Darker background for the card */
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3); /* More pronounced shadow */
                text-align: center;
                margin-top: -50px; /* Adjust this value to move the card up/down */
            }
            .login-card img {
                margin-bottom: 25px; /* Increased space below image */
                border-radius: 8px; /* Slightly rounded image corners */
            }
            .stTextInput label, .stTextInput div, .stButton {
                font-size: 1.1em; /* Slightly larger font for inputs/buttons */
            }
            .stButton button {
                background-color: #4CAF50; /* Green button */
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                border: none;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }
            .stButton button:hover {
                background-color: #45a049;
            }
        </style>
    """, unsafe_allow_html=True)

    # Use a container for the login card to apply centering
    with st.container():
        # Using columns to center the login card horizontally
        col1, col2, col3 = st.columns([1, 2, 1]) # Adjust ratios as needed

        with col2: # This column will contain the login form, effectively centering it
            #st.markdown("<div class='login-card'>", unsafe_allow_html=True)
            st.title("Sistema de Farmacia")
            st.subheader("Iniciar Sesión")

            # Image for the login page
            #futura imagen

            with st.form("login_form"):
                username = st.text_input("Usuario")
                password = st.text_input("Contraseña", type="password")

                submitted = st.form_submit_button("Ingresar")
                if submitted:
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = dict(user) # Store user as a dictionary
                        st.success(f"¡Bienvenido, {st.session_state.user['nombre']}!")
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos.")
            st.markdown("</div>", unsafe_allow_html=True)
        
    st.info("¿Olvidaste tu contraseña? Contacta al administrador del sistema para restablecerla.")


def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

# --- Funciones de Página ---

def show_dashboard():
    st.title("📊 Dashboard Principal")
    st.write(f"Bienvenido, {st.session_state.user['nombre']} ({st.session_state.user['rol']})")

    medicamentos = get_all_medicamentos_db()
    patients = get_all_patients_db()
    dispensations = get_all_dispensations_db()
    appointments = get_all_appointments_db()

    st.subheader("Estado General del Inventario")
    col1, col2, col3 = st.columns(3)
    
    total_medicamentos_distintos = len(medicamentos)
    total_stock = sum(m['stock_actual'] for m in medicamentos)
    emergency_stock = sum(m['stock_actual'] for m in medicamentos if m['solo_emergencia'] == 1)

    col1.metric("Total de Medicamentos Distintos", total_medicamentos_distintos)
    col2.metric("Stock Total de Unidades", total_stock)
    col3.metric("Stock Emergencia", emergency_stock)

    # Alertas de Bajo Stock
    low_stock_medicines = [m for m in medicamentos if m['stock_actual'] <= m['stock_minimo_alerta']]
    if low_stock_medicines:
        st.subheader("⚠️ Alertas de Bajo Stock")
        for med in low_stock_medicines:
            st.warning(f"**{med['nombre']}** ({med['presentacion']}) - Stock actual: {med['stock_actual']} (Mínimo: {med['stock_minimo_alerta']})")
    else:
        st.success("✅ No hay alertas de bajo stock en este momento.")

    # Alertas de Vencimiento
    today = datetime.now().date()
    # Medicamentos que vencen en 1 año o menos (y no han vencido aún)
    expiring_medicines = [m for m in medicamentos if datetime.strptime(m['fecha_vencimiento'], '%Y-%m-%d').date() <= today.replace(year=today.year + 1) and datetime.strptime(m['fecha_vencimiento'], '%Y-%m-%d').date() >= today]
    # Medicamentos que vencen en 3 meses o menos (y no han vencido aún)
    soon_expiring_medicines = [m for m in expiring_medicines if datetime.strptime(m['fecha_vencimiento'], '%Y-%m-%d').date() <= (today + pd.DateOffset(months=3)).date()]

    if soon_expiring_medicines:
        st.subheader("⏰ Alertas de Vencimiento Próximo (en los próximos 3 meses)")
        for med in soon_expiring_medicines:
            st.error(f"**{med['nombre']}** ({med['presentacion']}) - Vence el: {med['fecha_vencimiento']}")
    elif expiring_medicines:
        st.subheader("📅 Medicamentos con Vencimiento en el Próximo Año")
        for med in expiring_medicines:
            st.warning(f"**{med['nombre']}** ({med['presentacion']}) - Vence el: {med['fecha_vencimiento']}")
    else:
        st.info("👍 No hay medicamentos próximos a vencer en el próximo año.")

    st.subheader("Detalle del Inventario")
    df_medicamentos = pd.DataFrame(medicamentos)
    if not df_medicamentos.empty:
        df_medicamentos['solo_emergencia'] = df_medicamentos['solo_emergencia'].apply(lambda x: 'Sí' if x == 1 else 'No')
        st.dataframe(df_medicamentos[['codigo', 'nombre', 'presentacion', 'stock_actual', 'stock_minimo_alerta', 'fecha_vencimiento', 'fabricante', 'solo_emergencia']], use_container_width=True)
    else:
        st.info("No hay medicamentos registrados en el sistema.")

    # Admin specific dashboard features
    if st.session_state.user['rol'] == 'admin':
        st.markdown("---")
        st.subheader("Panel de Administración")

        # Total de pacientes
        st.metric("Total de Pacientes Registrados", len(patients))

        # Total de dispensaciones (Consultas) del Mes - Gráfico de línea
        st.write("### Tendencia de Dispensaciones Mensuales")
        if dispensations:
            df_disp = pd.DataFrame(dispensations)
            df_disp['fecha_dispensacion'] = pd.to_datetime(df_disp['fecha_dispensacion'])
            df_disp['mes_año'] = df_disp['fecha_dispensacion'].dt.to_period('M').astype(str)
            
            monthly_dispensations = df_disp.groupby('mes_año').size().reset_index(name='total_dispensaciones')
            monthly_dispensations['mes_año'] = pd.to_datetime(monthly_dispensations['mes_año']) # Convertir de nuevo para ordenar
            monthly_dispensations = monthly_dispensations.sort_values('mes_año') # Asegurar orden cronológico
            
            fig_monthly = px.line(
                monthly_dispensations,
                x='mes_año',
                y='total_dispensaciones',
                title='Número de Dispensaciones por Mes',
                labels={'mes_año': 'Mes y Año', 'total_dispensaciones': 'Número de Dispensaciones'},
                markers=True
            )
            fig_monthly.update_xaxes(dtick="M1", tickformat="%b\n%Y") # Formato de mes y año
            st.plotly_chart(fig_monthly, use_container_width=True)
        else:
            st.info("No hay dispensaciones registradas para mostrar la tendencia mensual.")

        # Rotación de medicamentos (top 5 más dispensados) - Gráfico de barras
        st.write("### Rotación de Medicamentos (Top 5 Más Dispensados)")
        if dispensations:
            df_disp = pd.DataFrame(dispensations)
            top_medicines = df_disp.groupby('medicamento_nombre')['cantidad_dispensada'].sum().nlargest(5).reset_index()
            top_medicines.rename(columns={'medicamento_nombre': 'Medicamento', 'cantidad_dispensada': 'Cantidad Total Dispensada'}, inplace=True)
            
            fig_top_meds = px.bar(
                top_medicines,
                x='Medicamento',
                y='Cantidad Total Dispensada',
                title='Top 5 Medicamentos Más Dispensados',
                labels={'Medicamento': 'Medicamento', 'Cantidad Total Dispensada': 'Unidades Dispensadas'},
                color='Cantidad Total Dispensada'
            )
            st.plotly_chart(fig_top_meds, use_container_width=True)
            st.dataframe(top_medicines, use_container_width=True) # Mantener la tabla también
        else:
            st.info("No hay dispensaciones registradas para calcular la rotación de medicamentos.")

        # Medicamentos próximos a vencer (para el administrador)
        st.write("### Medicamentos Próximos a Vencer (Administrador)")
        if expiring_medicines:
            df_expiring = pd.DataFrame(expiring_medicines)
            st.dataframe(df_expiring[['codigo', 'nombre', 'presentacion', 'fecha_vencimiento', 'stock_actual']], use_container_width=True)
        else:
            st.info("No hay medicamentos próximos a vencer.")

        # Medicamentos disponibles en emergencia (para el administrador)
        st.write("### Medicamentos Disponibles en Emergencia")
        emergency_medicines = [m for m in medicamentos if m['solo_emergencia'] == 1]
        if emergency_medicines:
            df_emergency = pd.DataFrame(emergency_medicines)
            st.dataframe(df_emergency[['codigo', 'nombre', 'presentacion', 'stock_actual', 'ubicacion_farmacia']], use_container_width=True)
        else:
            st.info("No hay medicamentos marcados como 'Solo para Emergencia'.")


        # Filtros de pacientes por síntomas/condiciones
        st.write("### Pacientes por Condiciones Médicas")
        all_conditions = set()
        for p in patients:
            if p['condiciones_medicas']:
                # Split by comma and strip whitespace, then add to set
                conditions_list = [c.strip() for c in p['condiciones_medicas'].split(',')]
                all_conditions.update(conditions_list)
        
        if all_conditions:
            selected_condition = st.selectbox("Filtrar por Condición Médica", ["Todas"] + sorted(list(all_conditions)))
            
            if selected_condition == "Todas":
                filtered_patients_by_condition = patients
            else:
                filtered_patients_by_condition = [p for p in patients if p['condiciones_medicas'] and selected_condition in [c.strip() for c in p['condiciones_medicas'].split(',')]]
            
            st.info(f"Número de pacientes con '{selected_condition}': **{len(filtered_patients_by_condition)}**")
            if filtered_patients_by_condition:
                df_filtered_patients = pd.DataFrame(filtered_patients_by_condition)
                st.dataframe(df_filtered_patients[['nombre_completo', 'cedula', 'condiciones_medicas']], use_container_width=True)
        else:
            st.info("No hay condiciones médicas registradas en los pacientes.")


def show_medicine_management():
    st.title("💊 Gestión de Medicamentos")
    st.write(f"Usuario actual: {st.session_state.user['nombre']} ({st.session_state.user['rol']})")

    # Control de acceso para añadir/editar/eliminar
    # 'admin' y 'farmacia' pueden añadir, modificar y eliminar medicamentos
    can_add_medicine = st.session_state.user['rol'] in ['admin', 'farmacia']
    can_modify_medicine = st.session_state.user['rol'] in ['admin', 'farmacia']
    can_delete_medicine = st.session_state.user['rol'] in ['admin', 'farmacia']

    # Restringir el acceso a esta página para el rol 'doctor'
    if st.session_state.user['rol'] == 'doctor':
        st.error("Acceso denegado. Los doctores solo pueden buscar medicamentos en la sección de 'Consulta Médica'.")
        return

    if can_add_medicine:
        st.subheader("Añadir Nuevo Medicamento")
        with st.form("add_medicine_form"):
            codigo = st.text_input("Código del Medicamento (Ej: 01160216)", max_chars=8).strip()
            nombre = st.text_input("Nombre del Medicamento").strip()
            principio_activo = st.text_input("Principio Activo").strip()
            presentacion = st.text_input("Presentación (Ej: Tabletas 500mg, Jarabe)").strip()
            stock_actual = st.number_input("Stock Actual", min_value=0, value=0)
            stock_minimo_alerta = st.number_input("Stock Mínimo para Alerta", min_value=0, value=10)
            # Para la fecha de vencimiento de un nuevo medicamento, el min_value es siempre hoy
            fecha_vencimiento = st.date_input("Fecha de Vencimiento", min_value=datetime.now().date()).strftime('%Y-%m-%d')
            solo_emergencia = st.checkbox("Solo para Emergencia")
            
            with st.expander("Campos Opcionales"):
                indicaciones = st.text_area("Indicaciones").strip()
                dosis_adultos = st.text_input("Dosis Adultos").strip()
                dosis_pediatricas = st.text_input("Dosis Pediátricas").strip()
                contraindicaciones = st.text_area("Contraindicaciones").strip()
                efectos_secundarios = st.text_area("Efectos Secundarios").strip()
                interacciones = st.text_area("Interacciones").strip()
                fabricante = st.text_input("Fabricante").strip()
                ubicacion_farmacia = st.text_input("Ubicación en Farmacia").strip()

            submitted = st.form_submit_button("Añadir Medicamento")
            if submitted:
                if codigo and nombre and principio_activo and presentacion:
                    if add_medicine_db(codigo, nombre, principio_activo, presentacion, stock_actual, stock_minimo_alerta, fecha_vencimiento, indicaciones, dosis_adultos, dosis_pediatricas, contraindicaciones, efectos_secundarios, interacciones, fabricante, ubicacion_farmacia, int(solo_emergencia)):
                        st.success(f"Medicamento '{nombre}' con código '{codigo}' añadido correctamente.")
                        st.rerun()
                else:
                    st.error("Los campos Código, Nombre, Principio Activo y Presentación son obligatorios.")
    else:
        st.info("Solo los administradores y farmacéuticos pueden añadir medicamentos.")

    st.subheader("Lista de Medicamentos")
    medicamentos = get_all_medicamentos_db()
    df_medicamentos = pd.DataFrame(medicamentos)

    if not df_medicamentos.empty:
        df_medicamentos['solo_emergencia'] = df_medicamentos['solo_emergencia'].apply(lambda x: 'Sí' if x == 1 else 'No')
        st.dataframe(df_medicamentos, use_container_width=True)

        if can_modify_medicine:
            st.subheader("Editar Medicamento")
            
            # Contenedor para la búsqueda y selección de medicamento a editar
            with st.container():
                search_term = st.text_input("Buscar medicamento por Código o Nombre para editar", key="edit_med_search_input").strip()
                
                selected_medicine = None
                medicine_options_for_select = {}

                if search_term:
                    filtered_medicines = [m for m in medicamentos if search_term.lower() in m['nombre'].lower() or search_term.lower() in m['codigo'].lower()]
                    
                    if filtered_medicines:
                        medicine_options_for_select = {m['id']: f"{m['nombre']} ({m['codigo']})" for m in filtered_medicines}
                        
                        if len(filtered_medicines) == 1:
                            selected_medicine = filtered_medicines[0]
                            st.info(f"Medicamento encontrado y seleccionado: **{selected_medicine['nombre']}** ({selected_medicine['codigo']})")
                        else:
                            selected_medicine_id = st.selectbox("Selecciona un medicamento de los resultados", 
                                                                options=list(medicine_options_for_select.keys()), 
                                                                format_func=lambda x: medicine_options_for_select[x], 
                                                                key="edit_med_select_filtered")
                            if selected_medicine_id:
                                selected_medicine = next((m for m in filtered_medicines if m['id'] == selected_medicine_id), None)
                    else:
                        st.info("No se encontraron medicamentos con ese código o nombre.")
                else:
                    st.info("Introduce un código o nombre para buscar un medicamento y editarlo.")

            if selected_medicine:
                with st.form("edit_medicine_form"):
                    st.write(f"Editando: **{selected_medicine['nombre']}** (Código: {selected_medicine['codigo']})")
                    
                    edit_codigo = st.text_input("Código", value=selected_medicine['codigo'], max_chars=8).strip()
                    edit_nombre = st.text_input("Nombre", value=selected_medicine['nombre']).strip()
                    edit_principio_activo = st.text_input("Principio Activo", value=selected_medicine['principio_activo']).strip()
                    edit_presentacion = st.text_input("Presentación", value=selected_medicine['presentacion']).strip()
                    edit_stock_actual = st.number_input("Stock Actual", min_value=0, value=selected_medicine['stock_actual'])
                    edit_stock_minimo_alerta = st.number_input("Stock Mínimo para Alerta", min_value=0, value=selected_medicine['stock_minimo_alerta'])
                    
                    current_date_venc = datetime.strptime(selected_medicine['fecha_vencimiento'], '%Y-%m-%d').date()
                    
                    # Fix para el error de fecha:
                    # Si la fecha de vencimiento actual es anterior a hoy, establece min_value a la fecha de vencimiento actual
                    # para evitar el error. De lo contrario, establece min_value a hoy.
                    min_date_for_edit_input = datetime.now().date()
                    if current_date_venc < min_date_for_edit_input:
                        min_date_for_edit_input = current_date_venc

                    edit_fecha_vencimiento = st.date_input("Fecha de Vencimiento", 
                                                           value=current_date_venc, 
                                                           min_value=min_date_for_edit_input).strftime('%Y-%m-%d')
                    edit_solo_emergencia = st.checkbox("Solo para Emergencia", value=bool(selected_medicine['solo_emergencia']))
                    
                    with st.expander("Campos Opcionales de Edición"):
                        indicaciones = st.text_area("Indicaciones", value=selected_medicine['indicaciones']).strip()
                        dosis_adultos = st.text_input("Dosis Adultos", value=selected_medicine['dosis_adultos']).strip()
                        dosis_pediatricas = st.text_input("Dosis Pediátricas", value=selected_medicine['dosis_pediatricas']).strip()
                        contraindicaciones = st.text_area("Contraindicaciones", value=selected_medicine['contraindicaciones']).strip()
                        efectos_secundarios = st.text_area("Efectos Secundarios", value=selected_medicine['efectos_secundarios']).strip()
                        interacciones = st.text_area("Interacciones", value=selected_medicine['interacciones']).strip()
                        fabricante = st.text_input("Fabricante", value=selected_medicine['fabricante']).strip()
                        ubicacion_farmacia = st.text_input("Ubicación en Farmacia", value=selected_medicine['ubicacion_farmacia']).strip()

                    submitted_edit = st.form_submit_button("Actualizar Medicamento")
                    if submitted_edit:
                        if edit_codigo and edit_nombre and edit_principio_activo and edit_presentacion:
                            if update_medicine_db(selected_medicine['id'], edit_codigo, edit_nombre, edit_principio_activo, edit_presentacion, edit_stock_actual, edit_stock_minimo_alerta, edit_fecha_vencimiento, indicaciones, dosis_adultos, dosis_pediatricas, contraindicaciones, efectos_secundarios, interacciones, fabricante, ubicacion_farmacia, int(edit_solo_emergencia)):
                                st.success(f"Medicamento '{edit_nombre}' actualizado correctamente.")
                                st.rerun()
                        else:
                            st.error("Los campos Código, Nombre, Principio Activo y Presentación son obligatorios.")
            else:
                st.info("Selecciona un medicamento para cargar sus detalles y editar.")

        if can_delete_medicine:
            st.subheader("Eliminar Medicamento")
            medicine_options_delete = {m['id']: f"{m['nombre']} ({m['codigo']})" for m in medicamentos}
            selected_medicine_id_delete = st.selectbox("Selecciona un medicamento para eliminar", options=list(medicine_options_delete.keys()), format_func=lambda x: medicine_options_delete[x] if x else "Selecciona...", key="delete_med_select")
            
            if selected_medicine_id_delete:
                # Asegurarse de que el botón de eliminación esté dentro de un formulario si no lo está ya
                with st.form("delete_medicine_form", clear_on_submit=True): # Añadir un formulario aquí si no está ya
                    st.write(f"¿Estás seguro de que quieres eliminar {medicine_options_delete[selected_medicine_id_delete]}?")
                    if st.form_submit_button(f"Confirmar Eliminación de {medicine_options_delete[selected_medicine_id_delete]}", help="Esto eliminará el medicamento permanentemente."):
                        delete_medicine_db(selected_medicine_id_delete)
                        st.success("Medicamento eliminado correctamente.")
                        st.rerun()
        else:
            st.info("Solo los administradores y farmacéuticos pueden editar o eliminar medicamentos.")
    else: # If not admin or farmacia, only view
        st.info("No tienes permisos para modificar medicamentos. Solo puedes ver la lista.")


def show_user_management():
    st.title("👥 Gestión de Usuarios")
    st.write(f"Usuario actual: {st.session_state.user['nombre']} ({st.session_state.user['rol']})")

    if st.session_state.user['rol'] != 'admin':
        st.error("Acceso denegado. Solo los administradores pueden gestionar usuarios.")
        return

    st.subheader("Añadir Nuevo Usuario")
    with st.form("add_user_form"):
        nombre = st.text_input("Nombre Completo").strip()
        usuario = st.text_input("Nombre de Usuario").strip()
        password = st.text_input("Contraseña", type="password").strip()
        rol = st.selectbox("Rol", ["doctor", "farmacia", "admin", "archivo"]) # Added 'archivo' role
        
        submitted = st.form_submit_button("Añadir Usuario")
        if submitted:
            if nombre and usuario and password:
                if add_user_db(nombre, usuario, password, rol):
                    st.success(f"Usuario '{nombre}' añadido correctamente.")
                    st.rerun()
            else:
                st.error("Todos los campos son obligatorios.")

    st.subheader("Lista de Usuarios")
    users = get_all_users_db()
    
    if users: # Check if users list is not empty
        df_users = pd.DataFrame(users)
        desired_user_columns = ['id', 'nombre', 'usuario', 'rol', 'activo', 'fecha_creacion']
        df_users = df_users.reindex(columns=desired_user_columns)
        st.dataframe(df_users, use_container_width=True)
    else:
        st.info("No hay usuarios registrados en el sistema (excepto el admin inicial).")

    if not df_users.empty: # Only proceed if there are users to edit/delete
        st.subheader("Editar Usuario")
        user_options = {u['id']: f"{u['nombre']} ({u['usuario']})" for u in users}
        selected_user_id = st.selectbox("Selecciona un usuario para editar", options=list(user_options.keys()), format_func=lambda x: user_options[x] if x else "Selecciona...")

        if selected_user_id:
            selected_user = next((u for u in users if u['id'] == selected_user_id), None)
            if selected_user:
                with st.form("edit_user_form"):
                    st.write(f"Editando: **{selected_user['nombre']}** (Usuario: {selected_user['usuario']})")
                    
                    edit_nombre = st.text_input("Nombre Completo", value=selected_user['nombre']).strip()
                    edit_usuario = st.text_input("Nombre de Usuario", value=selected_user['usuario']).strip()
                    edit_rol = st.selectbox("Rol", ["doctor", "farmacia", "admin", "archivo"], index=["doctor", "farmacia", "admin", "archivo"].index(selected_user['rol']))
                    edit_activo = st.checkbox("Activo", value=bool(selected_user['activo']))

                    submitted_edit = st.form_submit_button("Actualizar Usuario")
                    if submitted_edit:
                        if edit_nombre and edit_usuario:
                            if update_user_db(selected_user_id, edit_nombre, edit_usuario, edit_rol, int(edit_activo)):
                                st.success(f"Usuario '{edit_nombre}' actualizado correctamente.")
                                st.rerun()
                        else:
                            st.error("Nombre completo y nombre de usuario son obligatorios.")
                
                st.subheader("Restablecer Contraseña")
                with st.form("reset_password_form"):
                    new_password = st.text_input("Nueva Contraseña", type="password").strip()
                    confirm_password = st.text_input("Confirmar Nueva Contraseña", type="password").strip()
                    
                    submitted_reset = st.form_submit_button("Restablecer Contraseña")
                    if submitted_reset:
                        if new_password and new_password == confirm_password:
                            reset_user_password_db(selected_user_id, new_password)
                            st.success(f"Contraseña para '{selected_user['usuario']}' restablecida correctamente.")
                            st.rerun()
                        else:
                            st.error("Las contraseñas no coinciden o están vacías.")

        st.subheader("Eliminar Usuario")
        user_options_delete = {u['id']: f"{u['nombre']} ({u['usuario']})" for u in users}
        selected_user_id_delete = st.selectbox("Selecciona un usuario para eliminar", options=list(user_options_delete.keys()), format_func=lambda x: user_options_delete[x] if x else "Selecciona...", key="delete_user_select")
        
        if selected_user_id_delete:
            with st.form("delete_user_form", clear_on_submit=True): # Añadir un formulario aquí
                st.write(f"¿Estás seguro de que quieres eliminar {user_options_delete[selected_user_id_delete]}?")
                if st.form_submit_button(f"Confirmar Eliminación de {user_options_delete[selected_user_id_delete]}", help="Esto eliminará el usuario permanentemente."):
                    if selected_user_id_delete == st.session_state.user['id']:
                        st.error("No puedes eliminar tu propia cuenta.")
                    else:
                        delete_user_db(selected_user_id_delete)
                        st.success("Usuario eliminado correctamente.")
                        st.rerun()
    # else: # This else block is now handled by the initial `if users:` check
    #     st.info("No hay usuarios registrados en el sistema (excepto el admin inicial).")


def show_patient_management():
    st.title("🧑‍🤝‍🧑 Gestión de Pacientes y Citas") # Título actualizado para reflejar la gestión de citas
    st.write(f"Usuario actual: {st.session_state.user['nombre']} ({st.session_state.user['rol']})")

    # Roles que pueden modificar pacientes y citas: 'archivo' y 'admin'
    can_modify_patients = st.session_state.user['rol'] in ['archivo', 'admin']

    # Restringir el acceso a esta página para el rol 'doctor'
    if st.session_state.user['rol'] == 'doctor':
        st.error("Acceso denegado. Los doctores gestionan pacientes y citas desde la 'Consulta Médica'.")
        return

    if can_modify_patients:
        st.subheader("Añadir Nuevo Paciente")
        with st.form("add_patient_form"):
            nombre_completo = st.text_input("Nombre Completo del Paciente*").strip()
            cedula = st.text_input("Número de Cédula (Ej: 001-010180-0001X)*").strip()
            codigo_expediente = st.text_input("Código de Expediente/Tarjeta (Opcional)").strip()
            fecha_nacimiento = st.date_input("Fecha de Nacimiento*", min_value=datetime(1900, 1, 1).date()).strftime('%Y-%m-%d')
            telefono = st.text_input("Teléfono").strip()
            direccion = st.text_area("Dirección").strip()
            barrio = st.text_input("Barrio").strip()
            condiciones_medicas = st.text_area("Condiciones Médicas (separadas por coma)", help="Ej: Diabetes, Hipertensión, Asma").strip()

            submitted = st.form_submit_button("Añadir Paciente")
            if submitted:
                if nombre_completo and cedula and fecha_nacimiento:
                    if add_patient_db(nombre_completo, cedula, codigo_expediente, fecha_nacimiento, telefono, direccion, barrio, condiciones_medicas):
                        st.success(f"Paciente '{nombre_completo}' añadido correctamente.")
                        st.rerun()
                else:
                    st.error("Nombre Completo, Cédula y Fecha de Nacimiento son obligatorios.")
    else:
        st.info("No tienes permisos para añadir pacientes. Solo el rol 'Archivo' o 'Admin' puede hacerlo.")

    st.subheader("Lista de Pacientes")
    patients = get_all_patients_db()
    
    if patients:
        df_patients = pd.DataFrame(patients)
        # No se especificaron columnas exactas para esta tabla, se mostrarán todas por defecto
        st.dataframe(df_patients, use_container_width=True)
    else:
        st.info("No hay pacientes registrados en el sistema.")

    if not patients: # If no patients, no need to show edit/delete sections
        return

    if can_modify_patients:
        st.subheader("Editar Paciente")
        patient_options = {p['id']: f"{p['nombre_completo']} ({p['cedula']})" for p in patients}
        selected_patient_id = st.selectbox("Selecciona un paciente para editar", options=list(patient_options.keys()), format_func=lambda x: patient_options[x] if x else "Selecciona...", key="edit_patient_select_archive")

        if selected_patient_id:
            selected_patient = next((p for p in patients if p['id'] == selected_patient_id), None)
            if selected_patient:
                with st.form("edit_patient_form_archive"):
                    st.write(f"Editando: **{selected_patient['nombre_completo']}** (Cédula: {selected_patient['cedula']})")
                    
                    edit_nombre_completo = st.text_input("Nombre Completo*", value=selected_patient['nombre_completo']).strip()
                    edit_cedula = st.text_input("Cédula*", value=selected_patient['cedula']).strip()
                    edit_codigo_expediente = st.text_input("Código de Expediente/Tarjeta", value=selected_patient['codigo_expediente']).strip()
                    
                    current_date_nac = datetime.strptime(selected_patient['fecha_nacimiento'], '%Y-%m-%d').date()
                    edit_fecha_nacimiento = st.date_input("Fecha de Nacimiento*", value=current_date_nac, min_value=datetime(1900, 1, 1).date()).strftime('%Y-%m-%d')
                    
                    edit_telefono = st.text_input("Teléfono", value=selected_patient['telefono']).strip()
                    edit_direccion = st.text_area("Dirección", value=selected_patient['direccion']).strip()
                    edit_barrio = st.text_input("Barrio", value=selected_patient['barrio']).strip()
                    edit_condiciones_medicas = st.text_area("Condiciones Médicas (separadas por coma)", value=selected_patient['condiciones_medicas']).strip()

                    submitted_edit = st.form_submit_button("Actualizar Paciente")
                    if submitted_edit:
                        if edit_nombre_completo and edit_cedula and edit_fecha_nacimiento:
                            if update_patient_db(selected_patient_id, edit_nombre_completo, edit_cedula, edit_codigo_expediente, edit_fecha_nacimiento, edit_telefono, edit_direccion, edit_barrio, edit_condiciones_medicas):
                                st.success(f"Paciente '{edit_nombre_completo}' actualizado correctamente.")
                                st.rerun()
                            else:
                                st.error("Nombre Completo, Cédula y Fecha de Nacimiento son obligatorios.")

            st.subheader("Eliminar Paciente")
            patient_options_delete = {p['id']: f"{p['nombre_completo']} ({p['cedula']})" for p in patients}
            selected_patient_id_delete = st.selectbox("Selecciona un paciente para eliminar", options=list(patient_options_delete.keys()), format_func=lambda x: patient_options_delete[x] if x else "Selecciona...", key="delete_patient_select_archive")
            
            if selected_patient_id_delete:
                with st.form("delete_patient_form", clear_on_submit=True): # Añadir un formulario aquí
                    st.write(f"¿Estás seguro de que quieres eliminar {patient_options_delete[selected_patient_id_delete]}?")
                    if st.form_submit_button(f"Confirmar Eliminación de {patient_options_delete[selected_patient_id_delete]}", help="Esto eliminará el paciente permanentemente."):
                        delete_patient_db(selected_patient_id_delete)
                        st.success("Paciente eliminado correctamente.")
                        # Nota: La auditoría de eliminaciones de pacientes/citas no está implementada en una tabla separada.
                        # Actualmente, solo las modificaciones de dispensaciones tienen un log de auditoría.
                        st.rerun()
        else:
            st.info("No tienes permisos para modificar pacientes. Solo el rol 'Archivo' o 'Admin' puede hacerlo.")
    # else: # This else block is now handled by the initial `if patients:` check
    #     st.info("No hay pacientes registrados en el sistema.")

    st.markdown("---")
    # --- Gestión de Citas ---
    st.subheader("Gestión de Citas")
    st.write("Aquí puedes programar, editar y eliminar citas para los doctores.")

    # Solo los roles 'archivo' y 'admin' pueden gestionar citas
    if can_modify_patients: # Reutilizamos la misma lógica de permiso
        st.subheader("Programar Nueva Cita")
        doctors = get_doctors_db()
        
        if not patients:
            st.warning("No hay pacientes registrados. Por favor, añade pacientes primero para programar citas.")
            return
        if not doctors:
            st.warning("No hay doctores registrados. Por favor, añade doctores primero para programar citas.")
            return

        patient_options_for_appt = {p['id']: f"{p['nombre_completo']} ({p['cedula']})" for p in patients}
        doctor_options_for_appt = {d['id']: d['nombre'] for d in doctors}

        with st.form("add_appointment_form_archive"):
            selected_patient_id_appt = st.selectbox("Selecciona Paciente*", options=list(patient_options_for_appt.keys()), format_func=lambda x: patient_options_for_appt[x], key="add_appt_patient_select")
            selected_doctor_id_appt = st.selectbox("Selecciona Doctor*", options=list(doctor_options_for_appt.keys()), format_func=lambda x: doctor_options_for_appt[x], key="add_appt_doctor_select")
            
            appointment_date = st.date_input("Fecha de la Cita*", min_value=datetime.now().date())
            appointment_time = st.time_input("Hora de la Cita*", value=datetime.now().time())
            motivo_cita = st.text_area("Motivo de la Cita*").strip()
            
            submitted_appointment = st.form_submit_button("Programar Cita")
            if submitted_appointment:
                if selected_patient_id_appt and selected_doctor_id_appt and motivo_cita:
                    fecha_cita_str = f"{appointment_date.strftime('%Y-%m-%d')} {appointment_time.strftime('%H:%M')}"
                    if add_appointment_db(selected_patient_id_appt, selected_doctor_id_appt, fecha_cita_str, motivo_cita):
                        st.success("Cita programada correctamente.")
                        st.rerun()
                else:
                    st.error("Todos los campos marcados con * son obligatorios.")

        st.subheader("Lista de Citas")
        all_appointments = get_all_appointments_db()
        
        if all_appointments:
            df_all_appointments = pd.DataFrame(all_appointments)
            desired_all_appt_columns = ['paciente_nombre', 'doctor_nombre', 'fecha_cita', 'motivo_cita', 'estado_cita']
            df_all_appointments = df_all_appointments.reindex(columns=desired_all_appt_columns)
            st.dataframe(df_all_appointments, use_container_width=True)
        else:
            st.info("No hay citas registradas en el sistema.")

        if not all_appointments: # If no appointments, no need to show edit/delete sections
            return

        st.subheader("Editar Cita")
        appointment_edit_options = {
            a['id']: f"{a['paciente_nombre']} con {a['doctor_nombre']} el {a['fecha_cita']}"
            for a in all_appointments
        }
        selected_appointment_id_edit = st.selectbox("Selecciona una cita para editar", options=list(appointment_edit_options.keys()), format_func=lambda x: appointment_edit_options[x] if x else "Selecciona...", key="edit_appt_select_archive")

        if selected_appointment_id_edit:
            selected_appointment = get_appointment_by_id_db(selected_appointment_id_edit)
            if selected_appointment:
                with st.form("edit_appointment_form_archive"):
                    st.write(f"Editando cita para: **{appointment_edit_options[selected_appointment_id_edit]}**")

                    edit_patient_id_appt = st.selectbox("Paciente*", options=list(patient_options_for_appt.keys()), format_func=lambda x: patient_options_for_appt[x], index=list(patient_options_for_appt.keys()).index(selected_appointment['id_paciente']), key="edit_appt_patient_select")
                    edit_doctor_id_appt = st.selectbox("Doctor*", options=list(doctor_options_for_appt.keys()), format_func=lambda x: doctor_options_for_appt[x], index=list(doctor_options_for_appt.keys()).index(selected_appointment['id_doctor']), key="edit_appt_doctor_select")

                    current_date_appt = datetime.strptime(selected_appointment['fecha_cita'], '%Y-%m-%d %H:%M').date()
                    current_time_appt = datetime.strptime(selected_appointment['fecha_cita'], '%Y-%m-%d %H:%M').time()
                    
                    edit_appointment_date = st.date_input("Fecha de la Cita*", value=current_date_appt, min_value=datetime.now().date())
                    edit_appointment_time = st.time_input("Hora de la Cita*", value=current_time_appt)
                    edit_motivo_cita = st.text_area("Motivo de la Cita*", value=selected_appointment['motivo_cita']).strip()
                    edit_estado_cita = st.selectbox("Estado de la Cita", ["programada", "completada", "cancelada"], index=["programada", "completada", "cancelada"].index(selected_appointment['estado_cita']))

                    submitted_edit_appt = st.form_submit_button("Actualizar Cita")
                    if submitted_edit_appt:
                        if edit_patient_id_appt and edit_doctor_id_appt and edit_motivo_cita:
                            edit_fecha_cita_str = f"{edit_appointment_date.strftime('%Y-%m-%d')} {edit_appointment_time.strftime('%H:%M')}"
                            if update_appointment_db(selected_appointment_id_edit, edit_patient_id_appt, edit_doctor_id_appt, edit_fecha_cita_str, edit_motivo_cita, edit_estado_cita):
                                st.success("Cita actualizada correctamente.")
                                st.rerun()
                            else:
                                st.error("Error al actualizar cita.")
                        else:
                            st.error("Todos los campos marcados con * son obligatorios.")
            
            st.subheader("Eliminar Cita")
            appointment_delete_options = {
                a['id']: f"{a['paciente_nombre']} con {a['doctor_nombre']} el {a['fecha_cita']}"
                for a in all_appointments
            }
            selected_appointment_id_delete = st.selectbox("Selecciona una cita para eliminar", options=list(appointment_delete_options.keys()), format_func=lambda x: appointment_delete_options[x] if x else "Selecciona...", key="delete_appt_select_archive")

            if selected_appointment_id_delete:
                with st.form("delete_appointment_form", clear_on_submit=True): # Añadir un formulario aquí
                    st.write(f"¿Estás seguro de que quieres eliminar {appointment_delete_options[selected_appointment_id_delete]}?")
                    if st.form_submit_button(f"Confirmar Eliminación de {appointment_delete_options[selected_appointment_id_delete]}", help="Esto eliminará la cita permanentemente."):
                        delete_appointment_db(selected_appointment_id_delete)
                        st.success("Cita eliminada correctamente.")
                        st.rerun()
        # else: # This else block is now handled by the initial `if all_appointments:` check
        #     st.info("No hay citas registradas en el sistema.")
    else:
        st.info("No tienes permisos para gestionar citas. Solo el rol 'Archivo' o 'Admin' puede hacerlo.")


# --- Funciones de Gestión de Dispensaciones y Consulta Médica (para otros roles) ---

def show_dispensation_management():
    st.title("📦 Gestión de Dispensaciones")
    st.write(f"Usuario actual: {st.session_state.user['nombre']} ({st.session_state.user['rol']})")

    # Solo farmacia puede acceder a esta sección
    if st.session_state.user['rol'] != 'farmacia':
        st.error("Acceso denegado. Solo el rol 'Farmacia' puede gestionar dispensaciones.")
        return

    st.subheader("Registrar Nueva Dispensación")

    # Obtener listas de medicamentos, pacientes y doctores
    medicamentos = get_all_medicamentos_db()
    patients = get_all_patients_db()
    doctors = get_doctors_db()

    if not medicamentos:
        st.warning("No hay medicamentos registrados. Por favor, añada medicamentos primero.")
        return
    if not patients:
        st.warning("No hay pacientes registrados. Por favor, añada pacientes primero.")
        return
    if not doctors:
        st.warning("No hay doctores registrados. Por favor, añada doctores primero.")
        return

    medicine_options = {m['id']: f"{m['nombre']} ({m['presentacion']}) - Stock: {m['stock_actual']}" for m in medicamentos}
    patient_options = {p['id']: f"{p['nombre_completo']} (Cédula: {p['cedula']})" for p in patients}
    doctor_options = {d['id']: d['nombre'] for d in doctors}

    with st.form("add_dispensation_form"):
        # Búsqueda y selección de medicamento
        st.text_input("Buscar Medicamento por Nombre o Código", key="disp_med_search_input", on_change=lambda: st.session_state.__setitem__('selected_medicine_id_for_disp', None))
        
        filtered_medicines = [m for m in medicamentos if st.session_state.disp_med_search_input.lower() in m['nombre'].lower() or st.session_state.disp_med_search_input.lower() in m['codigo'].lower()]
        
        if filtered_medicines:
            # Si solo hay un resultado, seleccionarlo automáticamente
            if len(filtered_medicines) == 1 and not st.session_state.selected_medicine_id_for_disp:
                st.session_state.selected_medicine_id_for_disp = filtered_medicines[0]['id']
            
            # Mostrar selectbox con los resultados filtrados o todos si no hay búsqueda
            selected_medicine_id = st.selectbox(
                "Selecciona Medicamento*",
                options=list(medicine_options.keys()),
                format_func=lambda x: medicine_options[x],
                key="select_medicine_disp",
                index=list(medicine_options.keys()).index(st.session_state.selected_medicine_id_for_disp) if st.session_state.selected_medicine_id_for_disp in medicine_options else 0
            )
            st.session_state.selected_medicine_id_for_disp = selected_medicine_id
        else:
            st.warning("No se encontraron medicamentos. Por favor, añade medicamentos o ajusta tu búsqueda.")
            selected_medicine_id = None

        # Búsqueda y selección de paciente
        st.text_input("Buscar Paciente por Nombre o Cédula", key="disp_patient_search_input", on_change=lambda: st.session_state.__setitem__('selected_patient_id_for_disp', None))
        
        filtered_patients = [p for p in patients if st.session_state.disp_patient_search_input.lower() in p['nombre_completo'].lower() or st.session_state.disp_patient_search_input.lower() in p['cedula'].lower()]

        if filtered_patients:
            if len(filtered_patients) == 1 and not st.session_state.selected_patient_id_for_disp:
                st.session_state.selected_patient_id_for_disp = filtered_patients[0]['id']

            selected_patient_id = st.selectbox(
                "Selecciona Paciente*",
                options=list(patient_options.keys()),
                format_func=lambda x: patient_options[x],
                key="select_patient_disp",
                index=list(patient_options.keys()).index(st.session_state.selected_patient_id_for_disp) if st.session_state.selected_patient_id_for_disp in patient_options else 0
            )
            st.session_state.selected_patient_id_for_disp = selected_patient_id
        else:
            st.warning("No se encontraron pacientes. Por favor, añade pacientes o ajusta tu búsqueda.")
            selected_patient_id = None

        selected_doctor_id = st.selectbox("Selecciona Doctor*", options=list(doctor_options.keys()), format_func=lambda x: doctor_options[x])
        cantidad_dispensada = st.number_input("Cantidad a Dispensar*", min_value=1, value=1)
        motivo = st.text_area("Motivo de la Dispensación*").strip()
        notas_doctor = st.text_area("Notas del Doctor (Opcional)").strip()

        submitted = st.form_submit_button("Registrar Dispensación")
        if submitted:
            if selected_medicine_id and selected_patient_id and selected_doctor_id and cantidad_dispensada and motivo:
                if add_dispensation_db(selected_medicine_id, selected_patient_id, selected_doctor_id, cantidad_dispensada, motivo, notas_doctor):
                    st.success("Dispensación registrada correctamente.")
                    # No st.rerun() here, Streamlit handles it automatically after form submission
            else:
                st.error("Todos los campos marcados con * son obligatorios.")

    st.subheader("Historial de Dispensaciones")
    dispensations = get_all_dispensations_db()
    
    if dispensations:
        df_dispensations = pd.DataFrame(dispensations)
        desired_disp_history_columns = ['medicamento_nombre', 'paciente_nombre', 'doctor_nombre', 'cantidad_dispensada', 'fecha_dispensacion', 'motivo']
        df_dispensations = df_dispensations.reindex(columns=desired_disp_history_columns)
        st.dataframe(df_dispensations, use_container_width=True)
    else:
        st.info("No hay dispensaciones registradas en el sistema.")

    if not dispensations: # If no dispensations, no need to show edit/delete sections
        return

    st.subheader("Editar Dispensación")
    dispensation_options = {d['id']: f"{d['medicamento_nombre']} a {d['paciente_nombre']} el {d['fecha_dispensacion']}" for d in dispensations}
    selected_dispensation_id = st.selectbox("Selecciona una dispensación para editar", options=list(dispensation_options.keys()), format_func=lambda x: dispensation_options[x] if x else "Selecciona...", key="edit_disp_select")

    if selected_dispensation_id:
        selected_dispensation = next((d for d in dispensations if d['id'] == selected_dispensation_id), None)
        if selected_dispensation:
            with st.form("edit_dispensation_form"):
                st.write(f"Editando: **{dispensation_options[selected_dispensation_id]}**")
                
                edit_medicine_id = st.selectbox("Medicamento*", options=list(medicine_options.keys()), format_func=lambda x: medicine_options[x], index=list(medicine_options.keys()).index(selected_dispensation['id_medicamento']))
                edit_patient_id = st.selectbox("Paciente*", options=list(patient_options.keys()), format_func=lambda x: patient_options[x], index=list(patient_options.keys()).index(selected_dispensation['id_paciente']))
                edit_doctor_id = st.selectbox("Doctor*", options=list(doctor_options.keys()), format_func=lambda x: doctor_options[x], index=list(doctor_options.keys()).index(selected_dispensation['id_doctor']))
                edit_cantidad_dispensada = st.number_input("Cantidad a Dispensar*", min_value=1, value=selected_dispensation['cantidad_dispensada'])
                edit_motivo = st.text_area("Motivo de la Dispensación*", value=selected_dispensation['motivo']).strip()
                edit_notas_doctor = st.text_area("Notas del Doctor (Opcional)", value=selected_dispensation['notas_doctor']).strip()

                submitted_edit_disp = st.form_submit_button("Actualizar Dispensación")
                if submitted_edit_disp:
                    if edit_medicine_id and edit_patient_id and edit_doctor_id and edit_cantidad_dispensada and edit_motivo:
                        if update_dispensation_db(selected_dispensation_id, edit_medicine_id, edit_patient_id, edit_doctor_id, edit_cantidad_dispensada, edit_motivo, edit_notas_doctor, st.session_state.user['id'], st.session_state.user['nombre']):
                            st.success("Dispensación actualizada correctamente.")
                            st.rerun()
                    else:
                        st.error("Todos los campos marcados con * son obligatorios.")

    st.subheader("Eliminar Dispensación")
    dispensation_options_delete = {d['id']: f"{d['medicamento_nombre']} a {d['paciente_nombre']} el {d['fecha_dispensacion']}" for d in dispensations}
    selected_dispensation_id_delete = st.selectbox("Selecciona una dispensación para eliminar", options=list(dispensation_options_delete.keys()), format_func=lambda x: dispensation_options_delete[x] if x else "Selecciona...", key="delete_disp_select")
    
    if selected_dispensation_id_delete:
        with st.form("delete_dispensation_form", clear_on_submit=True):
            st.write(f"¿Estás seguro de que quieres eliminar {dispensation_options_delete[selected_dispensation_id_delete]}?")
            if st.form_submit_button(f"Confirmar Eliminación de {dispensation_options_delete[selected_dispensation_id_delete]}", help="Esto eliminará la dispensación permanentemente."):
                # La eliminación de dispensaciones no tiene un registro de auditoría visible para roles no admin.
                if delete_dispensation_db(selected_dispensation_id_delete):
                    st.success("Dispensación eliminada correctamente.")
                    st.rerun()
    # else: # This else block is now handled by the initial `if dispensations:` check
    #     st.info("No hay dispensaciones registradas en el sistema.")

    # Auditoría de Dispensaciones (solo para admin)
    if st.session_state.user['rol'] == 'admin':
        st.subheader("Registro de Auditoría de Dispensaciones")
        audit_logs = get_all_dispensation_audit_logs_db()
        if audit_logs:
            df_audit_logs = pd.DataFrame(audit_logs)
            st.dataframe(df_audit_logs, use_container_width=True)
        else:
            st.info("No hay registros de auditoría de dispensaciones.")


def show_doctor_consultation_page():
    st.title("👩‍⚕️👨‍⚕️ Consulta Médica")
    st.write(f"Usuario actual: {st.session_state.user['nombre']} ({st.session_state.user['rol']})")

    # Solo doctor puede acceder a esta sección
    if st.session_state.user['rol'] != 'doctor':
        st.error("Acceso denegado. Solo el rol 'Doctor' puede ver consultas médicas.")
        return

    st.subheader("Buscar Paciente para Consulta")
    search_patient_term = st.text_input("Buscar paciente por Nombre, Cédula o Código de Expediente", key="doc_patient_search_input").strip()

    patients = []
    if search_patient_term:
        patients = get_patient_by_search_term_db(search_patient_term)
        if not patients:
            st.info("No se encontraron pacientes con ese término de búsqueda.")
    else:
        st.info("Introduce un término de búsqueda para encontrar pacientes.")

    selected_patient = None
    if patients:
        patient_options = {p['id']: f"{p['nombre_completo']} (Cédula: {p['cedula']})" for p in patients}
        
        # Si solo hay un resultado, seleccionarlo automáticamente
        if len(patients) == 1 and not st.session_state.selected_patient_id_doc_consultation:
            st.session_state.selected_patient_id_doc_consultation = patients[0]['id']

        selected_patient_id = st.selectbox(
            "Selecciona un Paciente",
            options=list(patient_options.keys()),
            format_func=lambda x: patient_options[x],
            key="select_patient_doc_consultation",
            index=list(patient_options.keys()).index(st.session_state.selected_patient_id_doc_consultation) if st.session_state.selected_patient_id_doc_consultation in patient_options else 0
        )
        st.session_state.selected_patient_id_doc_consultation = selected_patient_id
        
        selected_patient = next((p for p in patients if p['id'] == selected_patient_id), None)

    if selected_patient:
        st.markdown("---")
        st.subheader(f"Detalles del Paciente: {selected_patient['nombre_completo']}")
        col1, col2 = st.columns(2)
        col1.write(f"**Cédula:** {selected_patient['cedula']}")
        col1.write(f"**Fecha de Nacimiento:** {selected_patient['fecha_nacimiento']}")
        col1.write(f"**Teléfono:** {selected_patient['telefono']}")
        col2.write(f"**Código de Expediente:** {selected_patient['codigo_expediente']}")
        col2.write(f"**Dirección:** {selected_patient['direccion']}")
        col2.write(f"**Barrio:** {selected_patient['barrio']}")
        st.write(f"**Condiciones Médicas:** {selected_patient['condiciones_medicas']}")

        st.markdown("---")
        st.subheader("Historial de Dispensaciones del Paciente")
        patient_dispensations = get_dispensations_by_patient_id_db(selected_patient['id'])
        
        if patient_dispensations:
            df_patient_disp = pd.DataFrame(patient_dispensations)
            desired_disp_columns = ['medicamento_nombre', 'presentacion', 'doctor_nombre', 'cantidad_dispensada', 'fecha_dispensacion', 'motivo', 'notas_doctor']
            df_patient_disp = df_patient_disp.reindex(columns=desired_disp_columns)
            st.dataframe(df_patient_disp, use_container_width=True)
        else:
            st.info("No hay dispensaciones registradas para este paciente.")

        st.markdown("---")
        st.subheader("Historial de Citas del Paciente")
        patient_appointments = get_appointments_by_patient_id_db(selected_patient['id'])
        
        if patient_appointments:
            df_patient_appt = pd.DataFrame(patient_appointments)
            desired_appt_columns = ['doctor_nombre', 'fecha_cita', 'motivo_cita', 'estado_cita']
            df_patient_appt = df_patient_appt.reindex(columns=desired_appt_columns)
            st.dataframe(df_patient_appt, use_container_width=True)
        else:
            st.info("No hay citas registradas para este paciente.")

        # Solo el rol 'doctor' puede añadir notas de consulta
        if st.session_state.user['rol'] == 'doctor':
            st.markdown("---")
            st.subheader("Añadir Notas de Consulta")
            with st.form("add_consultation_notes_form"):
                notas = st.text_area("Notas de la Consulta").strip()
                # Placeholder para el medicamento dado al paciente
                medicamentos_disponibles = get_all_medicamentos_db()
                medicine_options = {m['id']: f"{m['nombre']} ({m['presentacion']})" for m in medicamentos_disponibles}
                selected_med_given = st.selectbox("Medicamento Recetado (Opcional)", options=[None] + list(medicine_options.keys()), format_func=lambda x: medicine_options.get(x, "Ninguno"))

                if st.form_submit_button("Guardar Notas"):
                    # Aquí se integraría la lógica para guardar las notas de consulta
                    # Por ahora, solo mostraremos un mensaje de éxito.
                    if selected_med_given:
                        st.success(f"Notas de consulta y medicamento '{medicine_options[selected_med_given]}' guardados (funcionalidad de guardado no implementada en DB todavía).")
                    else:
                        st.success("Notas de consulta guardadas (funcionalidad de guardado no implementada en DB todavía).")
        else:
            st.info("Solo los doctores pueden añadir notas de consulta.")

    st.markdown("---")
    st.subheader("Buscar Medicamentos Disponibles")
    all_medicamentos = get_all_medicamentos_db()
    
    search_med_term = st.text_input("Buscar medicamento por Nombre o Código", key="doctor_med_search_input").strip()

    filtered_meds = []
    if search_med_term:
        filtered_meds = [m for m in all_medicamentos if search_med_term.lower() in m['nombre'].lower() or search_term.lower() in m['codigo'].lower()]
        if not filtered_meds:
            st.info("No se encontraron medicamentos con ese término de búsqueda.")
    else:
        filtered_meds = all_medicamentos # Mostrar todos si no hay búsqueda

    if filtered_meds:
        df_filtered_meds = pd.DataFrame(filtered_meds)
        df_filtered_meds['solo_emergencia'] = df_filtered_meds['solo_emergencia'].apply(lambda x: 'Sí' if x == 1 else 'No')
        st.dataframe(df_filtered_meds[['codigo', 'nombre', 'principio_activo', 'presentacion', 'stock_actual', 'fecha_vencimiento', 'fabricante', 'ubicacion_farmacia', 'solo_emergencia']], use_container_width=True)
    else:
        st.info("No hay medicamentos disponibles en el inventario.")


def show_archive_management():
    st.title("🗄️ Gestión de Archivo")
    st.write(f"Usuario actual: {st.session_state.user['nombre']} ({st.session_state.user['rol']})")

    # Esta página ya no es accesible para el rol 'archivo' directamente desde el menú.
    # Solo el admin podría verla si se la añadiera a su menú.
    st.error("Acceso denegado. Esta página no está disponible para su rol.")
    return


# --- Flujo de la Aplicación Streamlit ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None

# Inicializar los estados para los text_input de búsqueda si no existen
if 'disp_med_search_input' not in st.session_state:
    st.session_state.disp_med_search_input = ""
if 'disp_patient_search_input' not in st.session_state:
    st.session_state.disp_patient_search_input = ""
if 'doc_patient_search_input' not in st.session_state:
    st.session_state.doc_patient_search_input = ""
# Nuevo estado para la búsqueda de medicamentos del doctor
if 'doctor_med_search_input' not in st.session_state:
    st.session_state.doctor_med_search_input = ""


# Inicializar los IDs seleccionados para dispensación
if 'selected_medicine_id_for_disp' not in st.session_state:
    st.session_state.selected_medicine_id_for_disp = None
if 'selected_patient_id_for_disp' not in st.session_state:
    st.session_state.selected_patient_id_for_disp = None
if 'selected_patient_id_doc_consultation' not in st.session_state:
    st.session_state.selected_patient_id_doc_consultation = None


# Inyectar el CSS del tema oscuro directamente
st.markdown(dark_theme_css, unsafe_allow_html=True)

# Configurar el layout de la página para que sea ancho
st.set_page_config(layout="wide")


if not st.session_state.logged_in:
    login()
else:
    # Mostrar la barra lateral de navegación
    st.sidebar.title("Menú")

    # Opciones de menú según el rol del usuario
    if st.session_state.user['rol'] == 'admin':
        # Admin: Dashboard, Gestión de Medicamentos, Gestión de Usuarios, Gestión de Pacientes y Citas, Gestión de Dispensaciones
        page = st.sidebar.radio("Navegación", ["Dashboard", "Gestión de Medicamentos", "Gestión de Usuarios", "Gestión de Pacientes y Citas", "Gestión de Dispensaciones"])
    elif st.session_state.user['rol'] == 'farmacia':
        # Farmacia: Dashboard, Gestión de Medicamentos (puede editar emergencia/ubicación, añadir, ver), NO Dispensaciones, NO Consulta Médica
        page = st.sidebar.radio("Navegación", ["Dashboard", "Gestión de Medicamentos"])
    elif st.session_state.user['rol'] == 'doctor':
        # Doctor: Consulta Médica (ver pacientes, buscar medicamentos, añadir notas), NO Dispensaciones
        page = st.sidebar.radio("Navegación", ["Consulta Médica"])
    elif st.session_state.user['rol'] == 'archivo':
        # Archivo: Gestión de Pacientes y Citas (registrar, agendar, buscar, eliminar), NO Gestión de Archivo, NO Consulta Médica
        page = st.sidebar.radio("Navegación", ["Gestión de Pacientes y Citas"])
    else: # En caso de un rol no definido, mostrar solo dashboard
        page = st.sidebar.radio("Navegación", ["Dashboard"])


    st.sidebar.button("Cerrar Sesión", on_click=logout)

    # Mostrar la página seleccionada
    if page == "Dashboard":
        show_dashboard()
    elif page == "Gestión de Medicamentos":
        show_medicine_management()
    elif page == "Gestión de Usuarios":
        show_user_management()
    elif page == "Gestión de Pacientes y Citas": # Ahora esta página agrupa pacientes y citas
        show_patient_management()
    elif page == "Gestión de Dispensaciones":
        show_dispensation_management()
    elif page == "Consulta Médica":
        show_doctor_consultation_page()
    elif page == "Gestión de Archivo": # Esta página ahora es solo un placeholder con acceso denegado
        show_archive_management()
