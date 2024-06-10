import os
import re
import pdfplumber
from pdfminer.high_level import extract_text
import streamlit as st
from zipfile import ZipFile

# Function to extract text using pdfplumber
def extract_text_from_pdf_plumber(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text

# Function to extract text using pdfminer.six
def extract_text_from_pdf_miner(file_path):
    try:
        return extract_text(file_path)
    except Exception as e:
        st.error(f"Error extracting text with pdfminer.six: {str(e)}")
        return ""

# Main function to process and rename the PDF
def process_pdf(file_path):
    text = extract_text_from_pdf_plumber(file_path)
    initial_names = re.findall(r'\*([A-Za-z\u4E00-\u9FFF]+)\*', text)
    invoice_numbers = re.findall(r'\b\d{8}\b|\b\d{20}\b', text)
    amounts = [float(amount) for amount in re.findall(r'￥(\d+\.\d{2})', text) if amount]
    if not (initial_names and invoice_numbers and amounts):
        text = extract_text_from_pdf_miner(file_path)
        initial_names = re.findall(r'\*\*(.+?)\*\*', text)
        invoice_numbers = re.findall(r'\b\d{8}\b|\b\d{20}\b', text)
        amounts = [float(amount) for amount in re.findall(r'￥(\d+\.\d{2})', text) if amount]
    if initial_names and invoice_numbers and amounts:
        largest_amount = max(amounts)
        new_file_name = f"{initial_names[0]}_{invoice_numbers[0]}_{largest_amount:.2f}.pdf"
        new_file_path = os.path.join(os.path.dirname(file_path), new_file_name)
        os.rename(file_path, new_file_path)
        st.success(f"File renamed to: {new_file_name}")
        return new_file_path  # Return the new file path for the zip file
    else:
        st.error(f"Failed to extract all necessary information from: {file_path}")
        return None

# Function to create a zip file from a list of files
def create_zip(files, zip_name='processed_files.zip'):
    with ZipFile(zip_name, 'w') as zipf:
        for file in files:
            zipf.write(file, os.path.basename(file))
    return zip_name

# Streamlit interface
def main():
    st.title("PDF Invoice Renamer")
    uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)
    if st.button("Process"):
        if uploaded_files:
            processed_files = []
            for uploaded_file in uploaded_files:
                file_path = f"temp_{uploaded_file.name}"
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                new_file_path = process_pdf(file_path)
                if new_file_path:
                    processed_files.append(new_file_path)
            if processed_files:
                zip_file_path = create_zip(processed_files)
                with open(zip_file_path, "rb") as f:
                    st.download_button("Download All Processed Files", f, file_name=zip_file_path)
        else:
            st.warning("Please upload at least one PDF file.")

if __name__ == "__main__":
    main()
