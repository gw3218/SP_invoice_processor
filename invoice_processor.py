import os
import re
import pdfplumber
from pdfminer.high_level import extract_text
import streamlit as st

# Function to extract text using pdfplumber
def extract_text_from_pdf_plumber(file_path):
    with pdfplumber.open(file_path) as pdf:
        # Initialize an empty string to collect all the text
        text = ""
        # Loop through each page in the PDF
        for page in pdf.pages:
            # Extract text from the current page
            page_text = page.extract_text()
            if page_text:  # Check if text was found
                text += page_text + "\n"  # Append the text with a newline
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
    # First, try pdfplumber
    text = extract_text_from_pdf_plumber(file_path)

    # Check if key components are extracted
    initial_names = re.findall(r'\*([A-Za-z\u4E00-\u9FFF]+)\*', text)
    invoice_numbers = re.findall(r'\b\d{8}\b|\b\d{20}\b', text)
    amounts = [float(amount) for amount in re.findall(r'\d+\.\d{2}', text) if amount]

    # Fallback to pdfminer if components are missing
    if not (initial_names and invoice_numbers and amounts):
        text = extract_text_from_pdf_miner(file_path)
        initial_names = re.findall(r'\*\*(.+?)\*\*', text)
        invoice_numbers = re.findall(r'\b\d{8}\b|\b\d{20}\b', text)
        amounts = [float(amount) for amount in re.findall(r'\d+\.\d{2}', text) if amount]

    # Rename the file if all components are found
    if initial_names and invoice_numbers and amounts:
        largest_amount = max(amounts)
        new_file_name = f"{initial_names[0]}_{invoice_numbers[0]}_{largest_amount:.2f}.pdf"
        new_file_path = os.path.join(os.path.dirname(file_path), new_file_name)
        os.rename(file_path, new_file_path)
        st.success(f"File renamed to: {new_file_name}")
    else:
        st.error(f"Failed to extract all necessary information from: {file_path}")

# Streamlit interface
def main():
    st.title("PDF Invoice Renamer")
    
    uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)
    
    if st.button("Process"):
        if uploaded_files:
            for uploaded_file in uploaded_files:
                with open(uploaded_file.name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                process_pdf(uploaded_file.name)
        else:
            st.warning("Please upload at least one PDF file.")

if __name__ == "__main__":
    main()