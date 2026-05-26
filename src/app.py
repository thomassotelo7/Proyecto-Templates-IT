import streamlit as st
import streamlit.components.v1 as components
import json
import os

st.set_page_config(page_title="Plantillas Soporte IT", layout="wide")
st.title("📋 Central de Plantillas IT")

def boton_copiar(texto):
    html_code = f"""
    <style>
    body {{
        margin: 0;
        padding: 0;
        background-color: transparent;
    }}
    .btn {{
        width: 100%;
        height: 38px;
        background-color: transparent;
        color: #FAFAFA;
        border: 1px solid rgba(250, 250, 250, 0.2);
        border-radius: 0.5rem;
        cursor: pointer;
        font-family: "Source Sans Pro", sans-serif;
        font-size: 14px;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .btn:hover {{
        border-color: #FF4B4B; /* El rojo clásico de Streamlit */
        color: #FF4B4B;
    }}
    .btn:active {{
        transform: scale(0.95);
    }}
    </style>
    
    <textarea id="hidden-text" style="display:none;">{texto}</textarea>
    
    <button id="copy-btn" class="btn" onclick="copyText()">📋 Copiar</button>
    
    <script>
    function copyText() {{
        const text = document.getElementById("hidden-text").value;
        navigator.clipboard.writeText(text).then(() => {{
            const btn = document.getElementById("copy-btn");
            btn.innerHTML = "✅ ¡Copiado!";
            btn.style.borderColor = "#00CC66";
            btn.style.color = "#00CC66";
            
            // A los 2 segundos vuelve a la normalidad
            setTimeout(() => {{
                btn.innerHTML = "📋 Copiar";
                btn.style.borderColor = "rgba(250, 250, 250, 0.2)";
                btn.style.color = "#FAFAFA";
            }}, 2000);
        }});
    }}
    </script>
    """
    components.html(html_code, height=45)

@st.dialog("Vista Previa del Instructivo")
def mostrar_preview(titulo, texto):
    st.markdown(f"### {titulo}")
    
    html_preview = f"""
    <style>
    body {{
        margin: 0;
        padding: 0;
        background-color: transparent;
    }}
    textarea {{
        width: 100%;
        height: 280px;
        background-color: #262730; /* El color exacto del Dark Mode de Streamlit */
        color: #FAFAFA;
        border: 1px solid rgba(250, 250, 250, 0.2);
        border-radius: 0.5rem;
        padding: 12px;
        font-family: "Source Sans Pro", sans-serif;
        font-size: 16px;
        line-height: 1.6;
        resize: none;
        outline: none;
        box-sizing: border-box;
    }}
    textarea:focus {{
        border-color: #FF4B4B;
    }}
    </style>
    
    <textarea readonly>{texto}</textarea>
    """
    components.html(html_preview, height=290)

ruta_app = os.path.dirname(os.path.abspath(__file__))
ruta_json = os.path.join(ruta_app, "..", "plantillas", "plantillas.json")

try:
    with open(ruta_json, "r", encoding="utf-8") as f:
        plantillas = json.load(f)
except FileNotFoundError:
    st.error(f"No se encontró el archivo en: {ruta_json}")
    plantillas = {}

busqueda = st.text_input("🔍 Buscar instructivo...", "").lower()
st.divider()

plantillas_filtradas = {titulo: texto for titulo, texto in plantillas.items() if busqueda in titulo.lower()}

columnas_por_fila = 4
cols = st.columns(columnas_por_fila)

for i, (titulo, texto) in enumerate(plantillas_filtradas.items()):
    col_actual = cols[i % columnas_por_fila]
    
    with col_actual:
        with st.container(border=True):
            st.markdown(f'<div style="height: 55px; display: flex; align-items: center; overflow: hidden;"><b>{titulo}</b></div>', unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("👀 Preview", key=f"preview_{i}", use_container_width=True):
                    mostrar_preview(titulo, texto)
            
            with c2:
                boton_copiar(texto)