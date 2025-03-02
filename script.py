def extract_cuil(text, last_cuil, regex_pattern):
    matches = re.findall(regex_pattern, text)
    for match in matches:
        if match != '51763749' and match != last_cuil:
            return match
    return None

def split_pdf(input_pdf, last_cuil=None, file_name_template="{cuil}_Recibos_Gratificacion_2025-02.pdf", regex_pattern=r'\b\d{2}-(\d{8})-\d\b'):
    generated_files = []
    reader = PyPDF2.PdfReader(input_pdf)
    num_pages = len(reader.pages)

    for i in range(num_pages):
        page = reader.pages[i]
        text = page.extract_text()
        cuil = extract_cuil(text, last_cuil, regex_pattern)

        if cuil:
            last_cuil = cuil
            writer = PyPDF2.PdfWriter()
            writer.add_page(page)
            output_pdf = file_name_template.format(cuil=cuil)
            generated_files.append((output_pdf, writer))
        else:
            print(f'CUIL not found on page {i + 1}')
    return generated_files, last_cuil

def zip_pdfs(pdf_files, output_zip):
    with zipfile.ZipFile(output_zip, 'w') as zipf:
        for pdf_name, pdf_writer in pdf_files:
            pdf_bytes = BytesIO()
            pdf_writer.write(pdf_bytes)
            pdf_bytes.seek(0)
            zipf.writestr(pdf_name, pdf_bytes.read())