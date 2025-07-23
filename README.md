
<h1>Sistema de Gestión de Farmacia</h1>
<p>Este proyecto es una aplicación web desarrollada con <strong>Streamlit</strong>, diseñada para la gestión integral de una farmacia. Permite a diferentes roles de usuario administrar medicamentos, pacientes, citas y dispensaciones, optimizando los flujos de trabajo y el control de inventario.</p>
<p>Las funcionalidades clave incluyen:</p>
<ul>
    <li><strong>Gestión de Inventario:</strong> Control detallado de medicamentos, incluyendo stock, fechas de vencimiento y ubicación.</li>
    <li><strong>Gestión de Pacientes:</strong> Registro y administración de información de pacientes, incluyendo historial de dispensaciones y citas.</li>
    <li><strong>Gestión de Usuarios y Roles:</strong> Acceso diferenciado para administradores, farmacéuticos, doctores y personal de archivo.</li>
    <li><strong>Gestión de Citas:</strong> Programación y seguimiento de citas médicas.</li>
    <li><strong>Registro de Dispensaciones:</strong> Trazabilidad de la entrega de medicamentos y su impacto en el inventario.</li>
</ul>
<p>El sistema busca mejorar la eficiencia operativa y la seguridad en la gestión de recursos farmacéuticos y la atención al paciente.</p>

<h2>Características Principales</h2>
<ul>
    <li><strong>Acceso Basado en Roles (RBAC):</strong>
        <ul>
            <li><strong>Administrador:</strong> Control total sobre medicamentos, usuarios, pacientes, citas y dispensaciones. Acceso a dashboards y auditorías.</li>
            <li><strong>Farmacia:</strong> Gestión completa de medicamentos (añadir, editar, eliminar, ver stock y ubicación), y gestión de dispensaciones. No puede ver consultas médicas.</li>
            <li><strong>Doctor:</strong> Acceso a la información de pacientes (historial de dispensaciones y citas), búsqueda de medicamentos disponibles, y capacidad para añadir notas de consulta y el medicamento recetado. No puede gestionar dispensaciones ni pacientes/citas directamente.</li>
            <li><strong>Archivo:</strong> Gestión completa de pacientes (añadir, editar, eliminar) y citas (programar, editar, eliminar). No tiene acceso a la gestión de archivo (página específica), ni a la gestión de medicamentos o dispensaciones.</li>
        </ul>
    </li>
    <li><strong>Gestión de Medicamentos:</strong>
        <ul>
            <li>Registro, edición y eliminación de medicamentos.</li>
            <li>Control de stock actual y stock mínimo para alertas.</li>
            <li>Gestión de fechas de vencimiento con alertas visuales.</li>
            <li>Indicación de medicamentos "Solo para Emergencia" con su ubicación.</li>
            <li>Funcionalidad de búsqueda por código o nombre.</li>
        </ul>
    </li>
    <li><strong>Gestión de Pacientes:</strong>
        <ul>
            <li>Registro detallado de pacientes (nombre, cédula, fecha de nacimiento, contacto, dirección, condiciones médicas).</li>
            <li>Búsqueda de pacientes por nombre, cédula o código de expediente.</li>
            <li>Visualización del historial de dispensaciones y citas del paciente.</li>
        </ul>
    </li>
    <li><strong>Gestión de Citas:</strong>
        <ul>
            <li>Programación, edición y eliminación de citas con doctores.</li>
            <li>Seguimiento del estado de las citas (programada, completada, cancelada).</li>
        </ul>
    </li>
    <li><strong>Gestión de Dispensaciones:</strong>
        <ul>
            <li>Registro de la entrega de medicamentos a pacientes, con control de stock.</li>
            <li>Registro de auditoría para modificaciones en las dispensaciones (solo visible para administradores).</li>
        </ul>
    </li>
    <li><strong>Dashboard Interactivo:</strong>
        <ul>
            <li>Resumen del estado del inventario.</li>
            <li>Alertas de bajo stock y medicamentos próximos a vencer.</li>
            <li>Gráficos de tendencia de dispensaciones y rotación de medicamentos (para administradores).</li>
            <li>Filtro de pacientes por condiciones médicas (para administradores).</li>
        </ul>
    </li>
</ul>

<h2>Instalación</h2>
<p>Sigue estos pasos para configurar y ejecutar el proyecto en tu máquina local:</p>
<ol>
    <li><strong>Clona el repositorio:</strong>
        <pre><code>git clone https://github.com/tu_usuario_github/Sistema-Farmacia.git
cd Sistema-Farmacia</code></pre>
    </li>
    <li><strong>Crea un entorno virtual (recomendado):</strong>
        <pre><code>python -m venv venv

# En Windows
venv\Scriptsctivate

# En macOS/Linux
source venv/bin/activate</code></pre>
    </li>
    <li><strong>Instala las dependencias:</strong>
        <p>Asegúrate de tener el archivo <code>requirements.txt</code> en la raíz del proyecto con el siguiente contenido:</p>
        <pre><code>streamlit
bcrypt
pandas
plotly</code></pre>
        <p>Luego, instala las dependencias:</p>
        <pre><code>pip install -r requirements.txt</code></pre>
    </li>
    <li><strong>Ejecuta la aplicación Streamlit:</strong>
        <pre><code>streamlit run app.py</code></pre>
        <p>Esto abrirá la aplicación en tu navegador web por defecto (normalmente en <code>http://localhost:8501</code>).</p>
    </li>
</ol>

<h2>Uso</h2>
<p>Al iniciar la aplicación, serás redirigido a la página de inicio de sesión. Utiliza las credenciales apropiadas según el rol para acceder a las diferentes funcionalidades del sistema.</p>
<p><strong>Nota:</strong> Para la primera ejecución, si no tienes usuarios, puedes crear uno manualmente en la base de datos SQLite o tener un script de inicialización de usuarios (no incluido en este README).</p>

<h2>Tecnologías Utilizadas</h2>
<ul>
    <li><a href="https://www.python.org/">Python</a></li>
    <li><a href="https://streamlit.io/">Streamlit</a></li>
    <li><a href="https://www.sqlite.org/index.html">SQLite3</a></li>
    <li><a href="https://pypi.org/project/bcrypt/">bcrypt</a></li>
    <li><a href="https://pandas.pydata.org/">Pandas</a></li>
    <li><a href="https://plotly.com/python/">Plotly Express</a></li>
</ul>

<h2>Contribución</h2>
<p>Las contribuciones son bienvenidas. Si deseas mejorar este proyecto, por favor sigue estos pasos:</p>
<ol>
    <li>Haz un fork del repositorio.</li>
    <li>Crea una nueva rama (<code>git checkout -b feature/nueva-funcionalidad</code>).</li>
    <li>Realiza tus cambios y haz commit (<code>git commit -m 'feat: añade nueva funcionalidad'</code>).</li>
    <li>Sube tus cambios a tu fork (<code>git push origin feature/nueva-funcionalidad</code>).</li>
    <li>Abre un Pull Request.</li>
</ol>

<h2>Licencia</h2>
<p>Este proyecto está bajo la licencia MIT. Consulta el archivo <code>LICENSE</code> para más detalles.</p>
