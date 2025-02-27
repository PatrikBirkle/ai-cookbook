from docling.document_converter import DocumentConverter
from pathlib import Path
from utils.sitemap import get_sitemap_urls

converter = DocumentConverter()

# --------------------------------------------------------------
# Process all files in reports folder
# --------------------------------------------------------------

def process_reports_folder(input_folder: str = "reports", output_folder: str = "converted_outputs"):
    # Create Path objects
    input_dir = Path(input_folder)
    output_dir = Path(output_folder)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if input directory exists
    if not input_dir.exists():
        print(f"Input directory '{input_folder}' does not exist")
        return
    
    # Process all files in the directory
    documents = []
    # Process all files except hidden files
    for file_path in input_dir.glob("*"):
        if file_path.is_file() and not file_path.name.startswith('.'):
            print("\n" + "="*50)
            print(f"Processing: {file_path}")
            print("="*50)
            try:
                result = converter.convert(str(file_path))
                if result.document:
                    documents.append(result.document)
                    
                    # Create both markdown and JSON outputs
                    markdown_output = result.document.export_to_markdown()
                    json_output = result.document.export_to_dict()
                    
                    # Save markdown version
                    md_output_path = output_dir / f"{file_path.stem}.md"
                    md_output_path.write_text(markdown_output)
                    
                    # Save JSON version
                    json_output_path = output_dir / f"{file_path.stem}.json"
                    import json
                    json_output_path.write_text(json.dumps(json_output, indent=2))
                    
                    print(f"\nProcessed successfully!")
                    print(f"Markdown output saved to: {md_output_path}")
                    print(f"JSON output saved to: {json_output_path}")
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
    
    return documents

# Process the reports folder and save to converted_outputs
print("\nStarting document processing...")
documents = process_reports_folder()
print("\nProcessing complete! Check the 'converted_outputs' directory for the results.")

# --------------------------------------------------------------
# Basic PDF extraction
# --------------------------------------------------------------

result = converter.convert("https://arxiv.org/pdf/2408.09869")

document = result.document
markdown_output = document.export_to_markdown()
json_output = document.export_to_dict()

print(markdown_output)

# --------------------------------------------------------------
# Basic HTML extraction
# --------------------------------------------------------------

result = converter.convert("https://ds4sd.github.io/docling/")

document = result.document
markdown_output = document.export_to_markdown()
print(markdown_output)

# --------------------------------------------------------------
# Scrape multiple pages using the sitemap
# --------------------------------------------------------------

sitemap_urls = get_sitemap_urls("https://ds4sd.github.io/docling/")
conv_results_iter = converter.convert_all(sitemap_urls)

docs = []
for result in conv_results_iter:
    if result.document:
        document = result.document
        docs.append(document)
