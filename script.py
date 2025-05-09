import PyPDF2
import re
import zipfile
import os
from io import BytesIO

def extract_cuil(text, last_cuil, regex_pattern=r'\b\d{2}-(\d{8})-\d\b', exclude_match='51763749'):
    matches = re.findall(regex_pattern, text)
    for match in matches:
        if match != exclude_match and match != last_cuil:
            return match
    return None

def split_pdf(input_pdf, last_cuil=None, file_name_template="{cuil}_Recibos_Gratificacion_2025-02.pdf", regex_pattern=r'\b\d{2}-(\d{8})-\d\b', exclude_match='51763749', look_ahead_pages=0):
    generated_files = []
    reader = PyPDF2.PdfReader(input_pdf)
    num_pages = len(reader.pages)
    current_writer = None
    current_output_pdf = None

    i = 0
    while i < num_pages:
        page = reader.pages[i]
        text = page.extract_text()
        cuil = extract_cuil(text, last_cuil, regex_pattern, exclude_match)

        if cuil:
            # Found a new CUIL, create a new PDF
            last_cuil = cuil
            current_writer = PyPDF2.PdfWriter()
            current_writer.add_page(page)
            current_output_pdf = file_name_template.format(cuil=cuil)
            generated_files.append((current_output_pdf, current_writer))
            i += 1
        else:
            # No CUIL found on this page
            print(f'CUIL not found on page {i + 1}')

            # Check if we have a current writer (meaning we found a CUIL before)
            if current_writer and last_cuil:
                # Look ahead to see if any of the next n pages have a CUIL
                has_cuil_ahead = False

                # Only look ahead if we have enough pages left
                look_ahead_range = min(look_ahead_pages, num_pages - i - 1)

                for j in range(1, look_ahead_range + 1):
                    if i + j < num_pages:
                        ahead_page = reader.pages[i + j]
                        ahead_text = ahead_page.extract_text()
                        ahead_cuil = extract_cuil(ahead_text, last_cuil, regex_pattern, exclude_match)
                        if ahead_cuil:
                            has_cuil_ahead = True
                            break

                # If no CUIL found in the next n pages, add this page to the current PDF
                if not has_cuil_ahead:
                    current_writer.add_page(page)
                    i += 1
                else:
                    # There's a CUIL ahead, so we'll process this page in the next iteration
                    i += 1
            else:
                # No current writer or last_cuil, just skip this page
                i += 1
    return generated_files, last_cuil

def zip_pdfs(pdf_files, output_zip):
    with zipfile.ZipFile(output_zip, 'w') as zipf:
        for pdf_name, pdf_writer in pdf_files:
            pdf_bytes = BytesIO()
            pdf_writer.write(pdf_bytes)
            pdf_bytes.seek(0)
            zipf.writestr(pdf_name, pdf_bytes.read())
