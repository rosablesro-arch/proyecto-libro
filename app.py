import streamlit as st
from groq import Groq
from streamlit_quill import st_quill
import json
import os

# --- CONFIGURACIÓN DE PÁGINA PROFESIONAL ---
st.set_page_config(page_title="SISTEMA COLABORATIVO DE REDACCIÓN", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #ffffff; }
    
    /* Diseño de Hoja Blanca Estilo Word */
    .stQuill { 
        background: white !important; 
        border: 1px solid #cbd5e1 !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
        max-width: 850px; 
        margin: auto;
        border-radius: 4px;
        color: black !important;
    }
    
    /* Altura mínima para que parezca una hoja real */
    .ql-editor { min-height: 600px; font-size: 18px; line-height: 1.6; }

    /* Estilo de botones */
    .stButton>button { 
        border-radius: 8px; font-weight: bold; background-color: #3b82f6; color: white;
        width: 100%; border: none; height: 3em;
    }
    .stStatusWidget { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- GESTIÓN DE DATOS ---
DB_FILE = "libro_data.json"

def cargar_hojas():
    # Inicializa 100 hojas siempre
    base = {f"Hoja {i}": {"autor": "Nadie todavía", "texto": ""} for i in range(1, 101)}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            datos = json.load(f)
            base.update(datos)
    return base

# Carga inicial en la sesión
if 'diccionario_hojas' not in st.session_state:
    st.session_state.diccionario_hojas = cargar_hojas()

# --- INTERFAZ ---
st.title("📄 EDITOR DE HOJAS COMPARTIDO")

col_user, col_access = st.columns(2)
with col_user:
    nombre_usuario = st.text_input("👤 TU NOMBRE:", value="Estudiante")
with col_access:
    rol_usuario = st.selectbox("🔑 ROL EN EL PROYECTO:", ["Colaborador", "Coordinadora"])

st.write("---")

# Selección de Hoja
lista_de_hojas = list(st.session_state.diccionario_hojas.keys())
hoja_actual = st.selectbox("📖 SELECCIONA EL NÚMERO DE HOJA:", lista_de_hojas)

# --- LÓGICA DE INDEPENDENCIA ---
# Usamos una "key" única que incluye el nombre de la hoja. 
# Esto obliga a Streamlit a refrescar el contenido al cambiar de hoja.
st.subheader(f"📍 Editando ahora: {hoja_actual}")

texto_en_hoja = st_quill(
    value=st.session_state.diccionario_hojas[hoja_actual]["texto"],
    placeholder=f"Comienza a escribir la {hoja_actual}...",
    toolbar=[
        ['bold', 'italic', 'underline'],
        [{'color': []}, {'background': []}],
        [{'header': [1, 2, 3, False]}],
        [{'list': 'ordered'}, {'list': 'bullet'}],
        ['link', 'image'],
        ['clean']
    ],
    key=f"quill_{hoja_actual}" # CLAVE DINÁMICA: evita que se mezcle el texto
)

if st.button(f"💾 GUARDAR CAMBIOS EN {hoja_actual.upper()}"):
    # Registramos quién hizo el cambio
    st.session_state.diccionario_hojas[hoja_actual]["texto"] = texto_en_hoja
    st.session_state.diccionario_hojas[hoja_actual]["autor"] = nombre_usuario
    
    # Guardar en archivo para que no se pierda
    with open(DB_FILE, "w") as f:
        json.dump(st.session_state.diccionario_hojas, f)
    
    st.success(f"¡Hecho! La {hoja_actual} ha sido actualizada por {nombre_usuario}.")
    st.balloons()

st.write("---")

# --- MONITOR DE AUTORÍA (Lo que pediste) ---
with st.expander("🔍 REVISAR QUIÉN ESCRIBIÓ CADA HOJA"):
    st.info("Aquí verás el avance de todo el equipo en tiempo real.")
    for h in lista_de_hojas:
        info = st.session_state.diccionario_hojas[h]
        # Solo mostramos las hojas que ya tienen algo escrito
        if info['texto'] and info['texto'] != "<p><br></p>":
            st.markdown(f"✅ **{h}**")
            st.markdown(f"✍️ **Última edición por:** `{info['autor']}`")
            # Vista previa pequeña
            st.markdown(f"<div style='background: white; color: black; padding: 10px; border-radius: 5px;'>{info['texto']}</div>", unsafe_allow_html=True)
            st.write("---")

# --- DESCARGA FINAL ---
if rol_usuario == "Coordinadora":
    if st.button("🏗️ COMPILAR LIBRO PARA ENTREGA"):
        html_final = "<html><body style='font-family: Calibri, sans-serif;'>"
        for i in range(1, 101):
            h_id = f"Hoja {i}"
            contenido = st.session_state.diccionario_hojas[h_id]['texto']
            if contenido and contenido != "<p><br></p>":
                html_final += f"<div>{contenido}</div><div style='page-break-after:always;'></div>"
        html_final += "</body></html>"
        
        st.download_button("💾 DESCARGAR TRABAJO COMPLETO", html_final, file_name="Proyecto_Final_Hojas.html")
