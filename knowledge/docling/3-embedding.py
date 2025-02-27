from typing import List
import json
from pathlib import Path

import lancedb
from dotenv import load_dotenv
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from openai import OpenAI
import pandas as pd

load_dotenv()

# Initialize OpenAI client (make sure you have OPENAI_API_KEY in your environment variables)
client = OpenAI()

# Constants
CHUNKS_DIR = "chunks_output"  # Directory containing the chunk JSON files
DB_PATH = "data/lancedb"
TABLE_NAME = "docling"

# --------------------------------------------------------------
# Load chunks from JSON files
# --------------------------------------------------------------

def load_chunks():
    chunks = []
    chunks_dir = Path(CHUNKS_DIR)
    
    if not chunks_dir.exists():
        raise ValueError(f"Directory {CHUNKS_DIR} does not exist. Please run 2-chunking.py first.")
    
    for json_file in chunks_dir.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            file_chunks = json.load(f)
            # Keep the metadata exactly as it is in the JSON file
            chunks.extend(file_chunks)
    
    return chunks

def verify_table():
    """Verify the table exists and show some sample data"""
    try:
        # Connect to the database
        db = lancedb.connect(DB_PATH)
        
        # Try to open the table
        table = db.open_table(TABLE_NAME)
        
        # Get table info
        row_count = table.count_rows()
        print(f"\nTable verification:")
        print(f"- Found table '{TABLE_NAME}' with {row_count} rows")
        
        # Show a sample query
        print("\nSample data (first 2 rows):")
        df = table.to_pandas().head(2)
        for _, row in df.iterrows():
            print(f"\nText: {row['text'][:200]}...")
            print(f"Metadata: {row['metadata']}")
        
        return True
    except Exception as e:
        print(f"\nError accessing table: {str(e)}")
        return False

# --------------------------------------------------------------
# Create a LanceDB database and table
# --------------------------------------------------------------

# Create a LanceDB database
db = lancedb.connect(DB_PATH)

# Get the OpenAI embedding function
func = get_registry().get("openai").create(name="text-embedding-3-large")

# Define a simplified metadata schema
class ChunkMetadata(LanceModel):
    """
    You must order the fields in alphabetical order.
    This is a requirement of the Pydantic implementation.
    """
    filename: str | None
    page_numbers: List[int] | None
    title: str | None

# Define the main Schema
class Chunks(LanceModel):
    text: str = func.SourceField()
    vector: Vector(func.ndims()) = func.VectorField()  
    metadata: ChunkMetadata

# --------------------------------------------------------------
# Load and process chunks
# --------------------------------------------------------------

def explore_database():
    """Explore and display the content of the LanceDB database"""
    try:
        # Connect to the database
        db = lancedb.connect(DB_PATH)
        table = db.open_table(TABLE_NAME)
        
        # Get basic statistics
        row_count = table.count_rows()
        print("\n=== Database Content Overview ===")
        print(f"Total chunks: {row_count}")
        
        # Get the data as a pandas DataFrame
        df = table.to_pandas()
        
        # Show vector information
        print("\n=== Vector Information ===")
        vector_sample = df['vector'].iloc[0]
        print(f"Vector dimensions: {len(vector_sample)}")
        
        # Display full table content in a structured way
        print("\n=== Table Content ===")
        pd.set_option('display.max_colwidth', 50)  # Limit text column width for better display
        pd.set_option('display.max_rows', None)    # Show all rows
        
        # Create a more readable display DataFrame
        display_df = pd.DataFrame({
            'Text': df['text'].apply(lambda x: x[:50] + '...' if len(x) > 50 else x),
            'Vector (first 3 dims)': df['vector'].apply(lambda x: str(x[:3]) + '...'),
            'Metadata': df['metadata'].apply(str)
        })
        
        print(display_df.to_string())
        
        return True
    except Exception as e:
        print(f"\nError exploring database: {str(e)}")
        return False

def semantic_search(query: str, limit: int = 3):
    """Perform semantic search in the database"""
    try:
        db = lancedb.connect(DB_PATH)
        table = db.open_table(TABLE_NAME)
        
        print(f"\n=== Semantic Search: '{query}' ===")
        results = table.search(query).limit(limit).to_pandas()
        
        for idx, row in results.iterrows():
            print(f"\nMatch {idx + 1} (score: {row['_distance']:.4f}):")
            print(f"Text: {row['text'][:200]}...")
            print(f"Metadata: {row['metadata']}")
            
    except Exception as e:
        print(f"Error during search: {str(e)}")

def main():
    # Load chunks from JSON files
    chunks = load_chunks()

    if not chunks:
        print("No chunks found. Please run 2-chunking.py first to generate chunks.")
        return

    # Create or overwrite the table
    table = db.create_table(TABLE_NAME, schema=Chunks, mode="overwrite")
    
    # Add the chunks to the table (automatically embeds the text)
    print(f"Adding {len(chunks)} chunks to the database...")
    table.add(chunks)
    print("Done! Number of rows in table:", table.count_rows())
    
    # Verify and explore the database
    verify_table()
    explore_database()
    
    # Example semantic searches
    print("\n=== Additional Search Examples ===")
    semantic_search("Finanzen und Buchhaltung")
    semantic_search("Kontaktinformationen und Adressen")

if __name__ == "__main__":
    main()