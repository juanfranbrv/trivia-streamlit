import streamlit as st
from groq import Groq
import json

# Configuración de la página
st.set_page_config(page_title="Test App", page_icon="🤓", layout="wide")

# Inicializar estado para almacenar respuestas, preguntas y resultados
if 'preguntas' not in st.session_state:
    st.session_state.preguntas = []
    st.session_state.respuestas = {}
    st.session_state.submitted = False
    st.session_state.score = 0

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

    # Botón para generar un nuevo test
    if st.button("Generar Nuevo Test"):
        # Resetear el estado para generar un nuevo test
        st.session_state.preguntas = []
        st.session_state.respuestas = {}
        st.session_state.submitted = False
        st.session_state.score = 0

# Función para obtener una nueva pregunta desde Groq
def obtener_pregunta():
    try:
        # Configuración del cliente Groq
        groq_key = st.secrets["GROQ_API_KEY"]
        cliente = Groq(api_key=groq_key)

        # Creación de la solicitud a Groq
        chat_completion = cliente.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Responde en castellano. Hazme una pregunta tipo test sobre {selection}. "
                               f"El nivel de dificultad de la pregunta debe ser {nivel_dificultad}. "
                               f"Cada pregunta debe tener tres posibles respuestas. Tu respuesta debe estar en formato JSON y debe tener la pregunta del test, las tres posibles respuestas y la respuesta correcta como un número de índice 0, 1, o 2\n\n"
                               f"Tu respuesta debe ser única y exclusivamente el JSON. No incluyas nada más.\n"
                               f"Te pongo un ejemplo de JSON al que debes ceñirte\n\n{{\n  \"pregunta\": \"¿Cuál es el comportamiento de `st.experimental_memo` en Streamlit?\",\n  \"respuestas\": [\n    \"Almacena el resultado de una función en caché para mejorar el rendimiento, pero el caché se actualiza automáticamente cada vez que se vuelve a ejecutar la función.\",\n    \"Almacena el resultado de una función en caché de manera persistente, incluso si se cierra la aplicación Streamlit y se vuelve a abrir.\",\n    \"Almacena el resultado de una función en caché solo si los parámetros de entrada de la función no han cambiado, y permite el control manual sobre la actualización del caché.\"\n  ],\n  \"respuesta_correcta\": 2\n}}\n"
                }
            ],
            model="llama3-8b-8192",
        )

        # Intentar decodificar la respuesta como JSON
        pregunta = json.loads(chat_completion.choices[0].message.content)
        return pregunta

    except json.JSONDecodeError:
        # Simplemente retornar None si falla el decodificado, sin dejar un warning permanente
        return None
    except Exception as e:
        st.error(f"Error en la llamada a la API de Groq: {e}")
        return None

# Generar preguntas si no se han generado previamente
if not st.session_state.preguntas:
    with st.spinner('Generando preguntas, por favor espera...'):
        while len(st.session_state.preguntas) < 5:
            pregunta = obtener_pregunta()
            if pregunta:
                # Verificar la estructura del JSON para asegurar que contiene lo necesario
                if all(key in pregunta for key in ["pregunta", "respuestas", "respuesta_correcta"]) and len(pregunta["respuestas"]) == 3:
                    st.session_state.preguntas.append(pregunta)

# Mostrar preguntas y almacenar respuestas
if not st.session_state.submitted:
    for idx, pregunta in enumerate(st.session_state.preguntas):
        st.subheader(f"Pregunta {idx + 1}: {pregunta['pregunta']}")
        st.session_state.respuestas[idx] = st.radio(
            "Seleccione una respuesta:",
            options=range(len(pregunta['respuestas'])),
            format_func=lambda x: pregunta['respuestas'][x],
            key=f"pregunta_{idx}"
        )

    # Botón para corregir el test (colocado debajo de las preguntas)
    if st.button("Corregir Test"):
        st.session_state.submitted = True
        st.session_state.score = 0

        # Calcular puntuación
        for idx, pregunta in enumerate(st.session_state.preguntas):
            if st.session_state.respuestas[idx] == pregunta['respuesta_correcta']:
                st.session_state.score += 1

        # Recargar la página para mostrar solo los resultados
        st.rerun()
        st.session_state.submitted = True
        st.session_state.score = 0

        # Calcular puntuación
        for idx, pregunta in enumerate(st.session_state.preguntas):
            if st.session_state.respuestas[idx] == pregunta['respuesta_correcta']:
                st.session_state.score += 1

# Mostrar resultados si el test fue corregido
if st.session_state.submitted:
    st.header("Resultados del Test")
    st.write(f"Tu puntuación: {st.session_state.score} de {len(st.session_state.preguntas)}")

    # Mostrar cada pregunta con la respuesta seleccionada y la correcta
    for idx, pregunta in enumerate(st.session_state.preguntas):
        st.write(f"**Pregunta {idx + 1}:** {pregunta['pregunta']}")
        st.write(f"Tu respuesta: {pregunta['respuestas'][st.session_state.respuestas[idx]]}")
        st.write(f"Respuesta correcta: {pregunta['respuestas'][pregunta['respuesta_correcta']]}")

        if st.session_state.respuestas[idx] == pregunta['respuesta_correcta']:
            st.success("¡Correcto! ✅")
        else:
            st.error("Incorrecto ❌")
        # Ocultar el formulario después de corregir el test
        
