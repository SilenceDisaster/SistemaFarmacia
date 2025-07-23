# styles.py

dark_theme_css = """
<style>
    /* Asegura que el cuerpo de la aplicación ocupe todo el ancho disponible */
    .stApp {
        background-color: #2c3e50; /* Azul oscuro profundo */
        color: #ecf0f1; /* Texto claro para contraste */
        padding: 0 !important; /* Elimina el padding por defecto del cuerpo de la app */
        margin: 0 !important; /* Elimina el margen por defecto */
        width: 100vw; /* Ocupa el 100% del ancho del viewport */
        max-width: none; /* Elimina cualquier restricción de ancho máximo */
    }

    /* Contenedores principales de Streamlit: el contenido principal y el sidebar */
    /* Estas clases pueden variar ligeramente con las versiones de Streamlit, pero son comunes */
    .css-1d391kg, .css-fg4pbf, .main .block-container, .st-emotion-cache-z5fcl4 { /* Clases para el main content y otros contenedores */
        background-color: #34495e; /* Un azul oscuro ligeramente más claro */
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3); /* Sombra más pronunciada */
        padding: 20px;
        margin-bottom: 20px;
        max-width: 100% !important; /* Asegura que el contenido ocupe el 100% del espacio disponible */
        padding-left: 1rem; /* Ajusta el padding para que no esté demasiado pegado a los bordes */
        padding-right: 1rem;
    }
    
    /* Ajuste específico para el contenedor principal de la aplicación */
    .st-emotion-cache-z5fcl4 { /* Esta es una clase común para el contenedor principal del contenido */
        padding-left: 2rem; /* Más padding en los lados para un mejor aspecto general */
        padding-right: 2rem;
    }

    /* Títulos y subtítulos */
    h1, h2, h3, h4, h5, h6 {
        color: #ecf0f1; /* Blanco/gris claro para los encabezados */
    }

    /* Botones */
    .stButton>button {
        background-color: #3498db; /* Azul vibrante */
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        transition: background-color 0.3s ease, transform 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #2980b9; /* Azul más oscuro al pasar el ratón */
        transform: translateY(-2px);
    }
    .stButton>button:active {
        background-color: #1a5276;
        transform: translateY(0);
    }

    /* Inputs de texto y selectbox */
    .stTextInput>div>div>input, .stSelectbox>div>div>select, .stTextArea>div>div>textarea {
        border-radius: 8px;
        border: 1px solid #555555; /* Borde más oscuro */
        padding: 8px 12px;
        background-color: #2a3b4c; /* Fondo de input más oscuro para mejor contraste */
        color: #ffffff; /* Texto blanco puro para máxima visibilidad */
        width: 100%; /* Asegura que los inputs ocupen todo el ancho disponible */
    }
    .stTextInput>div>div>input:focus, .stSelectbox>div>div>select:focus, .stTextArea>div>div>textarea:focus {
        border-color: #3498db;
        box-shadow: 0 0 0 0.2rem rgba(52, 152, 219, 0.25);
    }

    /* Dataframes (tablas) */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        width: 100%; /* Asegura que la tabla ocupe todo el ancho disponible */
    }
    .stDataFrame table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed; /* Ayuda a que las columnas se ajusten */
    }
    .stDataFrame th {
        background-color: #4a6177; /* Azul oscuro para encabezados de tabla */
        color: #ecf0f1;
        padding: 12px 15px;
        text-align: left;
        border-bottom: 2px solid #555555;
    }
    .stDataFrame td {
        background-color: #34495e; /* Fondo de celda más oscuro */
        color: #ecf0f1;
        padding: 10px 15px;
        border-bottom: 1px solid #4a6177;
        word-break: break-word; /* Rompe palabras largas para evitar desbordamiento */
    }
    .stDataFrame tr:hover td {
        background-color: #40576e; /* Resaltar fila al pasar el ratón */
    }

    /* Mensajes de alerta/éxito/info */
    .stAlert {
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .stAlert.success {
        background-color: #28a74533; /* Verde con transparencia */
        color: #28a745;
        border-color: #28a745;
    }
    .stAlert.warning {
        background-color: #ffc10733; /* Naranja con transparencia */
        color: #ffc107;
        border-color: #ffc107;
    }
    .stAlert.error {
        background-color: #dc354533; /* Rojo con transparencia */
        color: #dc3545;
        border-color: #dc3545;
    }
    .stAlert.info {
        background-color: #17a2b833; /* Azul claro con transparencia */
        color: #17a2b8;
        border-color: #17a2b8;
    }

    /* Sidebar */
    .css-1lcbmhc { /* Clase específica del sidebar */
        background-color: #2c3e50; /* Fondo del sidebar más oscuro */
        border-right: 1px solid #34495e;
        box-shadow: 2px 0 5px rgba(0, 0, 0, 0.2);
    }
    .css-1lcbmhc .stRadio > label {
        color: #ecf0f1; /* Color de texto para las etiquetas de radio en el sidebar */
    }
    .css-1lcbmhc .stRadio > label > div {
        color: #ecf0f1; /* Asegura el color del texto de la opción seleccionada */
    }

    /* Login Container */
    .login-container {
        background-color: #34495e;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
        max-width: 500px;
        margin: 50px auto;
        text-align: center;
        color: #ecf0f1;
    }
    .login-container h1, .login-container h3 {
        color: #ecf0f1; /* Blanco para títulos de login */
        margin-bottom: 20px;
    }

    /* Ajustes para gráficos Plotly */
    .js-plotly-plot .plotly .modebar {
        background-color: #34495e !important; /* Fondo de la barra de herramientas de Plotly */
        color: #ecf0f1 !important;
    }
    .js-plotly-plot .plotly .modebar-btn {
        color: #ecf0f1 !important; /* Iconos de la barra de herramientas de Plotly */
    }
</style>
"""
