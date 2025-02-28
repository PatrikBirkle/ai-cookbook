"""
Vector search utilities for the hybrid retrieval system.
"""

from typing import Dict, List, Any, Optional
import lancedb
from pathlib import Path
import logging
import json

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
                
                logger.info(f"Result {idx+1}: filename={filename}, title={title}, score={row.get('_distance', 'N/A')}")

                # Build source citation
                source_parts = []
                
                # Try to extract a meaningful report name from the filename
                report_name = ""
                if filename:
                    # Remove file extension and path
                    report_name = filename.split('/')[-1]
                    report_name = report_name.split('.')[0]
                    # Replace underscores with spaces and capitalize
                    report_name = report_name.replace('_', ' ').title()
                    source_parts.append(report_name)
                
                # Add report type if available
                if report_type and report_type not in source_parts:
                    source_parts.append(report_type)
                
                # Add author if available
                if author:
                    source_parts.append(author)
                
                # Add date if available
                if date:
                    source_parts.append(date)
                
                # Add page numbers if available
                if isinstance(page_numbers, (list, tuple)) and len(page_numbers) > 0:
                    source_parts.append(f"p. {', '.join(str(p) for p in page_numbers)}")

                # Ensure we have a meaningful source name
                source_citation = ' - '.join([part for part in source_parts if part])
                if not source_citation:
                    source_citation = "Branchenreport"  # Default to "Branchenreport" if no specific source info
                
                # Build the complete source metadata
                source = f"\nSource: {source_citation}"
                
                # Add title if available and different from report name
                if title and title != report_name:
                    source += f"\nTitle: {title}"
                elif not title:
                    source += f"\nTitle: Branchenanalyse"

                text = row.get('text', '')
                if not text:
                    logger.warning(f"Result {idx+1} has no text content")
                    continue
                    
                contexts.append(f"{text}{source}")

            result = "\n\n".join(contexts)
            logger.info(f"Returning {len(result)} characters of context from vector search")
            logger.debug(f"Vector search context: {result[:500]}...")
            return result
            
        except Exception as e:
            logger.error(f"Error during vector search: {e}", exc_info=True)
            return "Error retrieving industry report data."
    
    return search_vector_db 