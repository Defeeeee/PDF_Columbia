import streamlit as st
from io import BytesIO
import zipfile
from script import extract_cuil, split_pdf, zip_pdfs

st.title('Procesador de archivos PDF')

uploaded_files = st.file_uploader("Subir Archivos PDF", type="pdf", accept_multiple_files=True)
file_name_template = st.text_input("Ingrese el nombre deseado de cada PDF.", "{dni}_Recibos_Vacaciones_2025-02.pdf")
zip_name = st.text_input("Ingrese el nombre deseado para el zip", "vacaciones.zip")

if st.button("Procesar"):
    if "{dni}" not in file_name_template:
        st.warning("El nombre de archivo debe contener {dni}.")
    if not file_name_template.endswith(".pdf"):
        st.warning("El nombre de archivo debe terminar en .pdf.")
    if not zip_name.endswith(".zip"):
        st.warning("El nombre del zip debe terminar en .zip.")
    elif uploaded_files:
        all_generated_files = []
        last_cuil = None

        for uploaded_file in uploaded_files:
            pdf_bytes = BytesIO(uploaded_file.read())
            generated_files, last_cuil = split_pdf(pdf_bytes, last_cuil, file_name_template.replace("{dni}", "{cuil}"))
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