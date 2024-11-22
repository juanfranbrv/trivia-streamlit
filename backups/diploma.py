import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# Configuración de la página
st.set_page_config(page_title="Generador de Diplomas", page_icon="🎓", layout="wide")

# Título de la aplicación
st.title("Generador de Diplomas")

# Sidebar para ingresar datos
with st.sidebar:
    username = "Juanfran"
    grade = "Dificil"
    difficulty_level = "Dificil"

# Función para generar el diploma
def generar_diploma(username, grade, difficulty_level):
    # Cargar la imagen base del diploma
    diploma_image = Image.open("diploma_template.jpg")
    draw = ImageDraw.Draw(diploma_image)

    # Configurar la fuente y el tamaño del texto
    font_username = ImageFont.truetype("times.ttf", 40)  # Cambiado a Times New Roman y tamaño reducido a la mitad
    font_details = ImageFont.truetype("times.ttf", 30)  # Cambiado a Times New Roman y tamaño reducido a la mitad

    # Posiciones para el texto
    username_position = (430, 290)
    tema_position = (300, 400)
 

    # Dibujar el texto en la imagen
    draw.text(username_position, username, font=font_username, fill="black")
    draw.text(tema_position, "este es el tema del test", font=font_username, fill="black")

    return diploma_image

# Botón para generar el diploma
if st.button("Generar Diploma"):
    if username and grade and difficulty_level:
        diploma_image = generar_diploma(username, grade, difficulty_level)
        st.image(diploma_image, caption="Diploma Generado", use_container_width=True)  # Cambiado a use_container_width
        st.success("¡Diploma generado con éxito!")
    else:
        st.error("Por favor, complete todos los campos.")

# Sección de depuración
st.write("Nombre de Usuario:", username)
st.write("Calificación:", grade)
st.write("Nivel de Dificultad:", difficulty_level)
