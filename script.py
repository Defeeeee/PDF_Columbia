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

def split_pdf(input_pdf, last_cuil=None, file_name_template="{cuil}_Recibos_Gratificacion_2025-02.pdf", regex_pattern=r'\b\d{2}-(\d{8})-\d\b', exclude_match='51763749', extra_pages=0):
    """
    Split a PDF file into multiple files based on CUIL numbers found in the pages.

    Args:
        input_pdf: The input PDF file (path or BytesIO object)
        last_cuil: The last CUIL processed (to avoid duplicates)
        file_name_template: Template for the output file names
        regex_pattern: Regex pattern to extract CUIL numbers
        exclude_match: CUIL number to exclude
        extra_pages: Number of extra pages without CUIL to include after a page with CUIL

    Returns:
        A tuple containing a list of (filename, PdfWriter) pairs and the last CUIL processed
    """
    generated_files = []
    reader = PyPDF2.PdfReader(input_pdf)
    num_pages = len(reader.pages)

    # Initialize variables
    i = 0
    current_pdf = None
    current_filename = None

    # Process each page in the PDF
    while i < num_pages:
        # Get the current page
        page = reader.pages[i]
        text = page.extract_text()
        cuil = extract_cuil(text, last_cuil, regex_pattern, exclude_match)

        if cuil:
            # Found a CUIL, start a new PDF
            if current_pdf is not None:
                # Add the previous PDF to the list of generated files
                generated_files.append((current_filename, current_pdf))

            # Create a new PDF
            current_pdf = PyPDF2.PdfWriter()
            current_pdf.add_page(page)
            current_filename = file_name_template.format(cuil=cuil)
            last_cuil = cuil

            # Move to the next page
            i += 1

            # Add extra pages without CUIL if requested
            extra_count = 0
            while extra_count < extra_pages and i < num_pages:
                next_page = reader.pages[i]
                next_text = next_page.extract_text()
                next_cuil = extract_cuil(next_text, last_cuil, regex_pattern, exclude_match)

                if next_cuil:
                    # Found another CUIL, stop adding extra pages
                    break

                # Add this page to the current PDF
                current_pdf.add_page(next_page)
                extra_count += 1
                i += 1
        else:
            # No CUIL found on this page
            if current_pdf is not None:
                # We have an active PDF, check if we should add this page to it
                # Look ahead to see if there's a CUIL in the next few pages
                has_cuil_ahead = False
                for j in range(1, min(extra_pages + 1, num_pages - i)):
                    ahead_page = reader.pages[i + j]
                    ahead_text = ahead_page.extract_text()
                    if extract_cuil(ahead_text, last_cuil, regex_pattern, exclude_match):
                        has_cuil_ahead = True
                        break

                if not has_cuil_ahead:
                    # No CUIL ahead, add this page to the current PDF
                    current_pdf.add_page(page)

            # Move to the next page
            i += 1

    # Add the last PDF to the list if it exists
    if current_pdf is not None:
        generated_files.append((current_filename, current_pdf))

    return generated_files, last_cuil

def zip_pdfs(pdf_files, output_zip):
    with zipfile.ZipFile(output_zip, 'w') as zipf:
        for pdf_name, pdf_writer in pdf_files:
            pdf_bytes = BytesIO()
            pdf_writer.write(pdf_bytes)
            pdf_bytes.seek(0)
            zipf.writestr(pdf_name, pdf_bytes.read())
