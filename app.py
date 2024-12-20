import streamlit as st
from groq import Groq
import json
from PIL import Image, ImageDraw, ImageFont
import io

# Configuración de la página
st.set_page_config(page_title="Test App", page_icon="🤓", layout="wide")

# Inicializar estado para almacenar respuestas, preguntas y resultados
if 'preguntas' not in st.session_state:
    st.session_state.preguntas = []
    st.session_state.respuestas = {}
    st.session_state.submitted = False
    st.session_state.score = 0

# Función para generar el diploma
def generar_diploma(username, grade, difficulty_level, tema_libre):
    # Cargar la imagen base del diploma
    diploma_image = Image.open("diploma_template.jpg")
    draw = ImageDraw.Draw(diploma_image)

    # Configurar la fuente y el tamaño del texto
    font_username = ImageFont.truetype("times.ttf", 40)  # Cambiado a Times New Roman y tamaño reducido a la mitad
    font_details = ImageFont.truetype("times.ttf", 30)  # Cambiado a Times New Roman y tamaño reducido a la mitad

    # Obtener el tamaño de la imagen
    image_width, image_height = diploma_image.size

    # Dibujar el nombre del usuario centrado
    text_username = username
    text_width, text_height = draw.textbbox((0, 0), text_username, font=font_username)[2:4]
    username_position = ((image_width - text_width) // 2, 290)
    draw.text(username_position, text_username, font=font_username, fill="black")

    # Dibujar el tema del test centrado
    text_tema = f"Tema: {tema_libre}"
    text_width, text_height = draw.textbbox((0, 0), text_tema, font=font_details)[2:4]
    tema_position = ((image_width - text_width) // 2, 400)
    draw.text(tema_position, text_tema, font=font_details, fill="black")

    return diploma_image

# Sidebar
with st.sidebar:
    st.image("logo_app.png", use_container_width=True)
    st.write("Responde a las 5 preguntas con el nivel máximo de dificultad para obtener el diploma")
    
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
    
    tema_libre = st.text_input("Tema libre", selection)

    # Campo para el nombre del usuario para el diploma
    nombre_usuario = st.text_input("Ingrese su nombre para el diploma")
    if not nombre_usuario:
        nombre_usuario = "Cabeza Huevo"

    # Botón para generar un nuevo test
    if st.button("Generar Nuevo Test"):
        # Resetear el estado para generar un nuevo test
        st.session_state.preguntas = []
        st.session_state.respuestas = {}
        st.session_state.submitted = False
        st.session_state.score = 0


    st.write("___")
   
    st.write("Made with 💖 by juanfranbrv")

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
                    "content": f"Responde en castellano. Hazme una pregunta tipo test sobre {tema_libre}. "
                               f"El nivel de dificultad de la pregunta debe ser {nivel_dificultad}. "
                               f"Cada pregunta debe tener tres posibles respuestas. Tu respuesta debe estar en formato JSON y debe tener la pregunta del test, las tres posibles respuestas y la respuesta correcta como un número de índice 0, 1, o 2\n\n"
                               f"Tu respuesta debe ser única y exclusivamente el JSON. No incluyas nada más.\n"
                               f"Te pongo un ejemplo de JSON al que debes ceñirte\n\n{{\n  \"pregunta\": \"¿Cuál es el comportamiento de st.experimental_memo en Streamlit?\",\n  \"respuestas\": [\n    \"Almacena el resultado de una función en caché para mejorar el rendimiento, pero el caché se actualiza automáticamente cada vez que se vuelve a ejecutar la función.\",\n    \"Almacena el resultado de una función en caché de manera persistente, incluso si se cierra la aplicación Streamlit y se vuelve a abrir.\",\n    \"Almacena el resultado de una función en caché solo si los parámetros de entrada de la función no han cambiado, y permite el control manual sobre la actualización del caché.\"\n  ],\n  \"respuesta_correcta\": 2\n}}\n"
                }
            ],
            model="llama3-8b-8192",
        )

        # Intentar decodificar la respuesta como JSON
        pregunta = json.loads(chat_completion.choices[0].message.content)
        print(pregunta['respuesta_correcta'])
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

# Mostrar resultados si el test fue corregido
if st.session_state.submitted:
    st.header("Resultados del Test")
    st.write(f"Tu puntuación: {st.session_state.score} de {len(st.session_state.preguntas)}")

    # Mostrar cada pregunta con la respuesta seleccionada y la correcta
    for idx, pregunta in enumerate(st.session_state.preguntas):
        st.write(f"**Pregunta {idx + 1}:** {pregunta['pregunta']}")
        st.write(f"Tu respuesta: {pregunta['respuestas'][st.session_state.respuestas[idx]]}")
        st.write(f"Respuesta correcta: {pregunta['respuestas'][pregunta['respuesta_correcta']]}")
        print(pregunta['respuesta_correcta'])

        if st.session_state.respuestas[idx] == pregunta['respuesta_correcta']:
            st.success("¡Correcto! ✅")
        else:
            st.error("Incorrecto ❌")

    # Generar diploma si el usuario acertó todas las preguntas en modo difícil
    if st.session_state.score == len(st.session_state.preguntas) and nivel_dificultad == "Dificil":
        if nombre_usuario:
            # Generar el diploma con la función existente
            diploma_image = generar_diploma(nombre_usuario, "", nivel_dificultad, tema_libre)
            st.image(diploma_image, caption="Diploma de Excelencia", use_container_width=True)

            # Permitir la descarga del diploma
            buf = io.BytesIO()
            diploma_image.save(buf, format="PNG")
            byte_im = buf.getvalue()

            st.download_button(
                label="Descargar Diploma",
                data=byte_im,
                file_name="diploma.png",
                mime="image/png"
            )
