import os
import argparse
from pypdf import PdfReader

def pdf_to_text(pdf_path, output_path=None):
    """
    Convert a PDF file to text format.
    
    Args:
        pdf_path (str): Path to the PDF file
        output_path (str, optional): Output text file path. If None, uses the same name as the PDF but with .txt extension
    
    Returns:
        str: Path to the created text file
    """
    # Extract the text from the PDF
    reader = PdfReader(pdf_path)
    text = ""
    
    print(f"Extracting text from {pdf_path}...")
    print(f"Total pages: {len(reader.pages)}")
    
    # Extract text from each page
    for i, page in enumerate(reader.pages):
        print(f"Processing page {i+1}/{len(reader.pages)}")
        text += page.extract_text() + "\n\n"
    
    # Create the output file path if not provided
    if output_path is None:
        output_path = os.path.splitext(pdf_path)[0] + ".txt"
    
    # Write the text to a file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    
    print(f"Text successfully extracted and saved to {output_path}")
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PDF files to text")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("-o", "--output", help="Output text file path (optional)")
    
    args = parser.parse_args()
    
    pdf_to_text(args.pdf_path, args.output)