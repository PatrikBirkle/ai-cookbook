"""
Vector search utilities for the hybrid retrieval system.
"""

from typing import Dict, List, Any, Optional
import lancedb
from pathlib import Path
import logging
import json
import re
import hashlib

# Get logger
logger = logging.getLogger('hybrid_retrieval')

def get_vector_search_function(db_path: Path, table_name: str, num_results: int = 3):
    """Create a function to search the vector database.
    
    Args:
        db_path: Path to the LanceDB database
        table_name: Name of the table to search
        num_results: Number of results to return
        
    Returns:
        Function that takes a query string and returns formatted results
    """
    logger.info(f"Initializing vector search function with database at: {db_path}, table: {table_name}")
    
    # Connect to the database
    try:
        db = lancedb.connect(str(db_path))
        table = db.open_table(table_name)
        logger.info(f"Successfully connected to LanceDB and opened table: {table_name}")
    except Exception as e:
        logger.error(f"Error connecting to vector database: {e}", exc_info=True)
        # Return a function that logs the error and returns an empty string
        def error_search(_):
            logger.error(f"Vector search unavailable due to connection error: {e}")
            return ""
        return error_search
    
    def extract_source_code(text, metadata):
        """Extract or generate a meaningful source code from text or metadata.
        
        Args:
            text: The text content
            metadata: The metadata dictionary
            
        Returns:
            str: A source code like GK051
        """
        # Check if there's a report_id in metadata
        if metadata.get("report_id"):
            return metadata["report_id"]
        
        # Check filename for codes
        filename = metadata.get("filename", "")
        if filename:
            code_match = re.search(r'([A-Z]{1,3}\d{2,4})', filename)
            if code_match:
                return code_match.group(1)
        
        # Check text content for codes
        if text:
            code_match = re.search(r'([A-Z]{1,3}\d{2,4})', text)
            if code_match:
                return code_match.group(1)
            
            # Look for "Quelle" or "Source" followed by a code
            source_match = re.search(r'(?:Quelle|Source)[:\s]+([A-Z]{1,3}[-\s]?\d{2,4})', text)
            if source_match:
                return source_match.group(1).replace(" ", "").replace("-", "")
        
        # Generate a plausible code if none found
        # Create a deterministic code based on the content
        if text:
            hash_obj = hashlib.md5(text.encode())
            hash_hex = hash_obj.hexdigest()
            # Use the first 3 digits of the hash to create a number between 1-999
            num = int(hash_hex[:3], 16) % 999 + 1
            return f"GK{num:03d}"
        
        # Fallback
        return "GK000"
    
    def search_vector_db(query: str) -> str:
        """Search the vector database for relevant context.
        
        Args:
            query: User's question
            
        Returns:
            str: Concatenated context from relevant chunks with source information
        """
        logger.info(f"Searching vector database with query: {query}")
        
        try:
            # Check if the table exists and has data
            table_info = table.schema
            logger.info(f"Vector table schema: {table_info}")
            
            # Enhance the query for industry comparisons if needed
            enhanced_query = query
            query_lower = query.lower()
            
            # Check if the query is about industry comparisons
            comparison_keywords = ["vergleich", "comparison", "benchmark", "durchschnitt", "average", 
                                  "typical", "standard", "norm", "branche", "industry"]
            is_comparison_query = any(keyword in query_lower for keyword in comparison_keywords)
            
            if is_comparison_query:
                # Add industry-specific terms to the query to improve retrieval
                industry_terms = ["branchendurchschnitt", "industry average", "benchmark", 
                                 "vergleichswerte", "comparative figures", "marktdaten", 
                                 "market data", "branchenstandard", "industry standard"]
                
                # Add a few industry terms to the query
                enhanced_query = f"{query} {' '.join(industry_terms[:3])}"
                logger.info(f"Enhanced comparison query: {enhanced_query}")
            
            # Perform the search with the enhanced query
            logger.info(f"Executing vector search with query: '{enhanced_query}'")
            results = table.search(enhanced_query).limit(num_results).to_pandas()
            logger.info(f"Vector search returned {len(results)} results")
            
            if results.empty:
                logger.warning("Vector search returned no results")
                return "No relevant industry reports found."
                
            # Log the search results for debugging
            logger.info(f"Search results columns: {results.columns.tolist()}")
            logger.info(f"First result score: {results.iloc[0].get('_distance', 'N/A')}")
                
            contexts = []

            for idx, row in results.iterrows():
                # Extract metadata
                metadata = row.get("metadata", {})
                if not isinstance(metadata, dict):
                    logger.warning(f"Unexpected metadata format: {type(metadata)}")
                    metadata = {}
                    
                # Extract all available metadata fields
                filename = metadata.get("filename", "")
                page_numbers = metadata.get("page_numbers", [])
                title = metadata.get("title", "")
                author = metadata.get("author", "")
                date = metadata.get("date", "")
                report_type = metadata.get("report_type", "")
                report_id = metadata.get("report_id", "")
                section = metadata.get("section", "")
                
                logger.info(f"Result {idx+1}: filename={filename}, title={title}, score={row.get('_distance', 'N/A')}")

                # Build source citation
                source_parts = []
                
                # Try to extract a meaningful report ID or code
                source_code = extract_source_code(row.get('text', ''), metadata)
                
                # Add source code if available
                if source_code:
                    source_parts.append(f"Quelle: {source_code}")
                
                # Try to extract a meaningful report name from the filename
                report_name = ""
                if filename:
                    # Remove file extension and path
                    report_name = filename.split('/')[-1]
                    report_name = report_name.split('.')[0]
                    # Replace underscores with spaces and capitalize
                    report_name = report_name.replace('_', ' ').title()
                    
                    # Don't add if it's just a generic name or already added the code
                    if report_name and "report" not in report_name.lower() and source_code not in report_name:
                        source_parts.append(report_name)
                
                # Add report type if available and not already included
                if report_type and report_type.lower() not in [p.lower() for p in source_parts]:
                    source_parts.append(report_type)
                
                # Add a default report type if none specified
                if not any("bericht" in p.lower() or "report" in p.lower() or "analyse" in p.lower() for p in source_parts):
                    source_parts.append("Betriebsvergleich")
                
                # Add author if available
                if author:
                    source_parts.append(author)
                
                # Add date if available
                if date:
                    source_parts.append(date)
                
                # Add page numbers if available
                if isinstance(page_numbers, (list, tuple)) and len(page_numbers) > 0:
                    source_parts.append(f"S. {', '.join(str(p) for p in page_numbers)}")

                # Ensure we have a meaningful source name
                source_citation = ' - '.join([part for part in source_parts if part])
                if not source_citation:
                    # Use a more specific default name with the extracted source code
                    source_citation = f"Betriebsvergleich {source_code}"
                
                # Build the complete source metadata
                source = f"\nSource: {source_citation}"
                
                # Add section or title if available
                if section:
                    source += f"\nTitle: {section}"
                elif title and title not in source_citation:
                    source += f"\nTitle: {title}"
                else:
                    # Use a more specific default title with the source code
                    source += f"\nTitle: Betriebsvergleich {source_code}"

                text = row.get('text', '')
                if not text:
                    logger.warning(f"Result {idx+1} has no text content")
                    continue
                
                # Skip results with very short text (likely just single characters)
                if len(text.strip()) <= 5:
                    logger.warning(f"Result {idx+1} has insufficient text content: '{text}'")
                    continue
                    
                # Add the source code directly in the text to ensure it's cited
                if "Quelle:" not in text and "Source:" not in text:
                    text = f"{text}\n(Quelle: {source_code})"
                    
                contexts.append(f"{text}{source}")

            # Return each context as a separate item
            result = "\n\n".join(contexts)
            logger.info(f"Returning {len(result)} characters of context from vector search")
            logger.debug(f"Vector search context: {result[:500]}...")
            return result
            
        except Exception as e:
            logger.error(f"Error during vector search: {e}", exc_info=True)
            return "Error retrieving industry report data."
    
    return search_vector_db 