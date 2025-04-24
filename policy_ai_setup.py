# policy_ai_setup.py — Manual metadata indexing with FAISS (resilient to BOM)

import os
import csv
import re
import pdfplumber
import pytesseract
from PIL import Image
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

# Settings
PDF_FOLDER = "./policy_pdfs"
REFERENCE_CSV = "policy_metadata_reference.csv"
EMBEDDINGS_PATH = "faiss_policy_index"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Load API key
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Load metadata from CSV (handles BOM or corrupt headers)
def load_metadata():
    metadata = {}
    if os.path.exists(REFERENCE_CSV):
        with open(REFERENCE_CSV, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Find the correct filename key even if BOM or weird formatting is present
                filename_key = next((key for key in row if key.lower().strip().startswith("filename")), None)
                if filename_key:
                    normalized = row[filename_key].strip().lower()
                    metadata[normalized] = row
                else:
                    print("⚠️ Skipping row due to missing 'Filename' column:", row)
    return metadata

# Ask user for missing metadata
def prompt_for_metadata(filename):
    print(f"\n📄 New file: {filename}")
    return {
        "Filename": filename,
        "Policy Number": input("   Policy Number (e.g. 11-010-00 or 'Unnumbered'): ").strip(),
        "Policy Name": input("   Policy Name: ").strip(),
        "Effective Date": input("   Effective Date (e.g. February 10, 2018): ").strip(),
        "Review Due Date": input("   Review Due Date (e.g. February 2024): ").strip(),
        "Document Type": input("   Document Type (Policy or Reference): ").strip()
    }

# Save updated metadata back to CSV
def save_metadata(metadata_dict):
    fieldnames = ["Filename", "Policy Number", "Policy Name", "Effective Date", "Review Due Date", "Document Type"]
    with open(REFERENCE_CSV, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in metadata_dict.values():
            writer.writerow(row)

# Extract and chunk PDFs
def extract_text_and_build_docs(metadata_dict):
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    all_docs = []

    for root, _, files in os.walk(PDF_FOLDER):
        for filename in sorted(files):
            if not filename.endswith(".pdf"):
                continue

            normalized = filename.strip().lower()
            full_path = os.path.join(root, filename)

            if normalized not in metadata_dict:
                metadata_dict[normalized] = prompt_for_metadata(filename)

            meta = metadata_dict[normalized]
            print(f"\n📄 Indexing: {filename}")

            try:
                with pdfplumber.open(full_path) as pdf:
                    full_text = ""
                    for page in pdf.pages:
                        text = page.extract_text()
                        if not text:
                            image = page.to_image(resolution=300)
                            text = pytesseract.image_to_string(image.original)
                        if text:
                            full_text += text + "\n"

                    chunks = splitter.split_text(full_text)
                    docs = [
                        Document(
                            page_content=chunk,
                            metadata={
                                "source": filename,
                                "policy_number": meta["Policy Number"],
                                "policy_name": meta["Policy Name"],
                                "effective_date": meta["Effective Date"].lstrip("'").strip(),
                                "review_due_date": meta["Review Due Date"].lstrip("'").strip(),
                                "document_type": meta["Document Type"]
                            }
                        )
                        for chunk in chunks
                    ]
                    all_docs.extend(docs)

            except Exception as e:
                print(f"❌ Failed to process {filename}: {e}")

    return all_docs

# Embed documents into FAISS
def build_faiss_index(documents):
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key, model="text-embedding-3-small")
    return FAISS.from_documents(documents, embeddings)

def save_index(index, path):
    index.save_local(path)

# Run indexing process
if __name__ == "__main__":
    print("📥 Loading metadata...")
    metadata_dict = load_metadata()

    print("📚 Extracting text and building document chunks...")
    documents = extract_text_and_build_docs(metadata_dict)

    print("💾 Saving updated metadata CSV...")
    save_metadata(metadata_dict)

    print(f"📊 {len(documents)} chunks generated. Creating FAISS index...")
    index = build_faiss_index(documents)

    print(f"✅ Saving index to '{EMBEDDINGS_PATH}'...")
    save_index(index, EMBEDDINGS_PATH)

    print("Indexing complete.")
