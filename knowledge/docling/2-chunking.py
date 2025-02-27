from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from dotenv import load_dotenv
from openai import OpenAI
from utils.tokenizer import OpenAITokenizerWrapper
import os
from pathlib import Path
import json

load_dotenv()

# Initialize OpenAI client (make sure you have OPENAI_API_KEY in your environment variables)
client = OpenAI()

# Constants
INPUT_DIR = "reports"  # Directory containing the PDF files
OUTPUT_DIR = "chunks_output"    # Directory to store the chunks
tokenizer = OpenAITokenizerWrapper()  # Load our custom tokenizer for OpenAI
MAX_TOKENS = 8191  # text-embedding-3-large's maximum context length

def ensure_directory(directory):
    """Create directory if it doesn't exist"""
    Path(directory).mkdir(parents=True, exist_ok=True)

def process_file(file_path):
    """Process a single PDF file and return its chunks"""
    converter = DocumentConverter()
    result = converter.convert(str(file_path))
    
    chunker = HybridChunker(
        tokenizer=tokenizer,
        max_tokens=MAX_TOKENS,
        merge_peers=True,
    )
    
    chunk_iter = chunker.chunk(dl_doc=result.document)
    chunks = list(chunk_iter)
    
    # Extract page numbers for each chunk
    processed_chunks = []
    for chunk in chunks:
        # Get page numbers from the chunk's provenance information
        page_numbers = []
        for item in chunk.meta.doc_items:
            for prov in item.prov:
                if hasattr(prov, 'page_no') and prov.page_no is not None:
                    page_numbers.append(prov.page_no)
        
        # Remove duplicates and sort page numbers
        page_numbers = sorted(list(set(page_numbers))) if page_numbers else None
        
        # Create the chunk dictionary with metadata
        chunk_dict = {
            'text': chunk.text,
            'metadata': {
                'filename': Path(file_path).stem,
                'page_numbers': page_numbers,
                'title': chunk.meta.headings[0] if chunk.meta.headings else None
            }
        }
        processed_chunks.append(chunk_dict)
    
    return processed_chunks

def save_chunks(chunks, original_filename, output_dir):
    """Save chunks to a JSON file"""
    # Remove .pdf extension if present and don't append _chunks
    base_name = Path(original_filename).stem
    output_file = Path(output_dir) / f"{base_name}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

def main():
    # Ensure output directory exists
    ensure_directory(OUTPUT_DIR)
    
    # Get all PDF files in the input directory
    input_files = list(Path(INPUT_DIR).glob('*.pdf'))
    
    if not input_files:
        print(f"No PDF files found in {INPUT_DIR}")
        return
    
    # Process each PDF file
    for file_path in input_files:
        try:
            print(f"Processing {file_path}...")
            chunks = process_file(file_path)
            save_chunks(chunks, file_path.name, OUTPUT_DIR)
            print(f"Successfully processed {file_path}. Chunks saved to {OUTPUT_DIR}")
            # Print first chunk to verify page numbers are captured
            if chunks:
                print(f"Sample chunk metadata: {chunks[0]['metadata']}")
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")

if __name__ == "__main__":
    main()
