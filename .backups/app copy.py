import streamlit as st
from groq import Groq
import json

# Configuración de la página
st.set_page_config(page_title="Test App", page_icon="🧠", layout="wide")

# Sidebar
with st.sidebar:
    st.button("Botón")

    nivel_dificultad = st.select_slider(
        "Nivel de dificultad",
        options=[
            "Facil",
            "Intermedio",
            "Dificil",
        ],
    )

    options = ["Programación de lenguaje natural", "LLMs : Modelos extensos de lenguaje", "Python", "Streamlit"]
    selection = st.radio("Temas propuestos", options)
    
    title = st.text_input("Movie title", selection)

# Inicialización de variables de estado
if 'pregunta_actual' not in st.session_state:
    st.session_state.pregunta_actual = None
if 'respuestas_totales' not in st.session_state:
    st.session_state.respuestas_totales = 0
if 'respuestas_correctas' not in st.session_state:
    st.session_state.respuestas_correctas = 0
if 'respuestas_incorrectas' not in st.session_state:
    st.session_state.respuestas_incorrectas = 0
if 'respuesta_seleccionada' not in st.session_state:
    st.session_state.respuesta_seleccionada = False
if 'disabled_botones' not in st.session_state:
    st.session_state.disabled_botones = False

# Función para obtener una nueva pregunta
def obtener_pregunta():
    groq_key = st.secrets["GROQ_API_KEY"]
    cliente = Groq(api_key=groq_key)

    chat_completion = cliente.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Responde en castellano. Hazme una pregunta tipo test sobre {selection}. El nivel de dificultad de la pregunta debe ser {nivel_dificultad}. Cada pregunta debe tener tres posibles respuestas. Tu respuesta debe estar en formato JSON y debe tener la pregunta del test, las tres posibles respuestas y la respuesta correcta como un número de índice 0, 1, o 2\n\nTu respuesta debe ser única y exclusivamente el JSON. No incluyas nada más.\nTe pongo un ejemplo de JSON al que debes ceñirte\n\n{{\n  \"pregunta\": \"¿Cuál es el comportamiento de `st.experimental_memo` en Streamlit?\",\n  \"respuestas\": [\n    \"Almacena el resultado de una función en caché para mejorar el rendimiento, pero el caché se actualiza automáticamente cada vez que se vuelve a ejecutar la función.\",\n    \"Almacena el resultado de una función en caché de manera persistente, incluso si se cierra la aplicación Streamlit y se vuelve a abrir.\",\n    \"Almacena el resultado de una función en caché solo si los parámetros de entrada de la función no han cambiado, y permite el control manual sobre la actualización del caché.\"\n  ],\n  \"respuesta_correcta\": 2\n}}\n"
            }
        ],
        model="llama3-8b-8192",
    )

    try:
        # Intentar decodificar la respuesta como JSON
        pregunta = json.loads(chat_completion.choices[0].message.content)
        return pregunta
    except json.JSONDecodeError as e:
        st.error(f"Error al decodificar la respuesta JSON: {e}")
        st.write(f"Respuesta recibida: {chat_completion.choices[0].message.content}")
        return None

# Función para manejar la respuesta del usuario
def manejar_respuesta(respuesta_usuario):
    st.session_state.respuestas_totales += 1
    if respuesta_usuario == st.session_state.pregunta_actual['respuesta_correcta']:
        st.session_state.respuestas_correctas += 1
        st.success("¡Respuesta correcta!")
    else:
        st.session_state.respuestas_incorrectas += 1
        st.error(f"Respuesta incorrecta. La respuesta correcta era: {st.session_state.pregunta_actual['respuestas'][st.session_state.pregunta_actual['respuesta_correcta']]}")

    # Marcar que se ha seleccionado una respuesta y deshabilitar los botones
    st.session_state.respuesta_seleccionada = True
    st.session_state.disabled_botones = True

# Botón para comenzar el test
if st.button("Comenzar test"):
    st.session_state.pregunta_actual = obtener_pregunta()
    st.session_state.respuesta_seleccionada = False
    st.session_state.disabled_botones = False

# Mostrar la pregunta actual
if st.session_state.pregunta_actual:
    st.write(f"Pregunta: {st.session_state.pregunta_actual['pregunta']}")
    for i, respuesta in enumerate(st.session_state.pregunta_actual['respuestas']):
        if st.button(respuesta, key=f"respuesta_{i}", disabled=st.session_state.disabled_botones):
            manejar_respuesta(i)

    # Botón para avanzar a la siguiente pregunta, habilitado solo si ya se seleccionó una respuesta
    if st.session_state.respuesta_seleccionada:
        if st.button("Siguiente pregunta"):
            st.session_state.pregunta_actual = obtener_pregunta()
            st.session_state.respuesta_seleccionada = False
            st.session_state.disabled_botones = False

# Barra de progreso
st.write("Progreso del test:")
st.progress(st.session_state.respuestas_totales)
st.write(f"Respuestas totales: {st.session_state.respuestas_totales}")
st.write(f"Respuestas correctas: {st.session_state.respuestas_correctas}")
st.write(f"Respuestas incorrectas: {st.session_state.respuestas_incorrectas}")

# Resumen final
if st.session_state.respuestas_totales > 0:
    st.write("Resumen final:")
    st.write(f"Respuestas totales: {st.session_state.respuestas_totales}")
    st.write(f"Respuestas correctas: {st.session_state.respuestas_correctas}")
    st.write(f"Respuestas incorrectas: {st.session_state.respuestas_incorrectas}")
    st.write(f"Porcentaje de aciertos: {st.session_state.respuestas_correctas / st.session_state.respuestas_totales * 100:.2f}%")

# Sección de depuración
if st.session_state.pregunta_actual:
    st.write("Respuesta JSON recibida:")
    st.json(st.session_state.pregunta_actual)
