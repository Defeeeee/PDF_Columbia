import streamlit as st
from io import BytesIO
import zipfile
import re
from script import extract_cuil, split_pdf, zip_pdfs

st.title('Procesador de archivos PDF')

uploaded_files = st.file_uploader("Subir Archivos PDF", type="pdf", accept_multiple_files=True)
file_name_template = st.text_input("Ingrese el nombre deseado de cada PDF.", "{dni}_Recibos_Vacaciones_2025-02.pdf")
zip_name = st.text_input("Ingrese el nombre deseado para el zip", "vacaciones.zip")

with st.expander("Opciones avanzadas"):
    regex_pattern = st.text_input("Ingrese el patrón de regex para CUIL", r'\b\d{2}-(\d{8})-\d\b')
    exclude_match = st.text_input("Ingrese el valor a excluir", "51763749")
    look_ahead_pages = st.number_input("Number of pages to look ahead for CUIL detection ", min_value=0, value=0, step=1, help="If a page doesn't have a CUIL, check this many pages ahead. If none of them have a CUIL, associate the page with the last detected CUIL.")

    try:
        re.compile(regex_pattern)
        regex_valid = True
    except re.error:
        st.warning("El patrón de regex no es válido.")
        regex_valid = False

if st.button("Procesar"):
    if "{dni}" not in file_name_template:
        st.warning("El nombre de archivo debe contener {dni}.")
    if not file_name_template.endswith(".pdf"):
        st.warning("El nombre de archivo debe terminar en .pdf.")
    if not zip_name.endswith(".zip"):
        st.warning("El nombre del zip debe terminar en .zip.")
    elif not regex_valid:
        st.warning("Por favor ingrese un patrón de regex válido.")

    elif uploaded_files:
        all_generated_files = []
        last_cuil = None

        for uploaded_file in uploaded_files:
            pdf_bytes = BytesIO(uploaded_file.read())
            generated_files, last_cuil = split_pdf(pdf_bytes, last_cuil, file_name_template.replace("{dni}", "{cuil}"), regex_pattern, exclude_match, look_ahead_pages)
            all_generated_files.extend(generated_files)

        if len(all_generated_files) > 0:
            zip_buffer = BytesIO()
            zip_pdfs(all_generated_files, zip_buffer)
            zip_buffer.seek(0)

            st.download_button(
                label="Descargar ZIP",
                data=zip_buffer,
                file_name=zip_name,
                mime="application/zip"
            )
        else:
            st.warning("No se encontraron CUILs en los archivos PDF.")
    else:
        st.warning("Por favor suba al menos un archivo PDF.")