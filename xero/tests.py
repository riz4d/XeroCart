from django.test import TestCase

# Create your tests here.
import fitz

def count_pages(pdf_path):
    try:
        pdf_document = fitz.open(pdf_path)
        num_pages = pdf_document.page_count
        pdf_document.close()

        return num_pages

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    pdf_path = './media/info/ibm_QkZOufI.pdf'
    result = count_pages(pdf_path)
    if result is not None:
        print(f"The PDF file '{pdf_path}' has {result} pages.")
    else:
        print("Failed to count pages. Please check the provided PDF file path.")
