import streamlit as st
from io import BytesIO
import zipfile
from script import extract_cuil, split_pdf, zip_pdfs

st.title('PDF Processor')

uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)
file_name_template = st.text_input("Enter the filename template (use {cuil} for CUIL)", "{cuil}_Recibos_Gratificacion_2025-02.pdf")
zip_name = st.text_input("Enter the name for the final zip file", "vacaciones.zip")

if st.button("Process and Download"):
    if uploaded_files:
        all_generated_files = []
        last_cuil = None

        for uploaded_file in uploaded_files:
            pdf_bytes = BytesIO(uploaded_file.read())
            generated_files, last_cuil = split_pdf(pdf_bytes, last_cuil, file_name_template)
            all_generated_files.extend(generated_files)

        zip_buffer = BytesIO()
        zip_pdfs(all_generated_files, zip_buffer)
        zip_buffer.seek(0)

        st.download_button(
            label="Download ZIP",
            data=zip_buffer,
            file_name=zip_name,
            mime="application/zip"
        )
    else:
        st.warning("Please upload at least one PDF file.")