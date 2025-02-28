import pandas as pd
import os
from pathlib import Path
import logging
from typing import Dict, List, Any, Optional
import re

# Configure logging
logger = logging.getLogger('hybrid_retrieval')

def get_excel_files(financials_dir: Path) -> List[Path]:
    """Get all Excel files in the financials directory.
    
    Args:
        financials_dir: Path to the financials directory
        
    Returns:
        List of paths to Excel files
    """
    logger.info(f"Looking for Excel files in: {financials_dir}")
    excel_files = list(financials_dir.glob("*.xlsx"))
    logger.info(f"Found {len(excel_files)} Excel files: {[f.name for f in excel_files]}")
    return excel_files

def read_excel_file(file_path: Path) -> pd.DataFrame:
    """Read an Excel file into a pandas DataFrame.
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        pandas DataFrame
    """
    try:
        logger.info(f"Reading Excel file: {file_path.name}")
        df = pd.read_excel(file_path)
        logger.info(f"Successfully read Excel file: {file_path.name}, shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Error reading Excel file {file_path.name}: {e}")
        return pd.DataFrame()

def query_excel_data(financials_dir: Path, query_text: str) -> Dict[str, pd.DataFrame]:
    """Query Excel files based on the query text.
    
    Args:
        financials_dir: Path to the financials directory
        query_text: User's question text
    
    Returns:
        dict: Dictionary with file names as keys and pandas DataFrames as values
    """
    logger.info(f"Querying Excel data for: {query_text}")
    
    # Get all Excel files
    excel_files = get_excel_files(financials_dir)
    
    results = {}
    
    # Determine which files might be relevant to the query
    relevant_files = []
    query_lower = query_text.lower()
    
    # Map of keywords to file patterns
    keyword_to_file = {
        "bilanz": "Bilanz",
        "balance": "Bilanz",
        "gewinn": "Gewinn",
        "verlust": "Verlust",
        "profit": "Gewinn",
        "loss": "Verlust",
        "income": "Gewinn",
        "umsatz": "Entwicklung Bruttoumsatz",
        "revenue": "Entwicklung Bruttoumsatz",
        "sales": "Entwicklung Bruttoumsatz",
        "liquidität": "Liquidität",
        "liquidity": "Liquidität",
        "cash": "Liquidität",
        "zahlungsverhalten": "Entwicklung Zahlungsverhalten",
        "payment": "Entwicklung Zahlungsverhalten",
        "kostenstelle": "Kostenstellenanalyse",
        "cost center": "Kostenstellenanalyse",
        "soll-ist": "Soll-Ist Vergleich",
        "target-actual": "Soll-Ist Vergleich",
        "budget": "Soll-Ist Vergleich"
    }
    
    # Check if any keywords are in the query
    for keyword, file_pattern in keyword_to_file.items():
        if keyword in query_lower:
            # Find files that match the pattern
            matching_files = [f for f in excel_files if file_pattern in f.name]
            relevant_files.extend(matching_files)
    
    # If no specific files matched, use all files
    if not relevant_files:
        logger.info("No specific files matched the query, using all files")
        relevant_files = excel_files
    else:
        # Remove duplicates
        relevant_files = list(set(relevant_files))
        logger.info(f"Relevant files: {[f.name for f in relevant_files]}")
    
    # Read each relevant file
    for file_path in relevant_files:
        df = read_excel_file(file_path)
        if not df.empty:
            results[file_path.name] = df
    
    return results

def format_excel_data(results: Dict[str, pd.DataFrame]) -> str:
    """Format Excel data for display.
    
    Args:
        results: Dictionary with file names as keys and pandas DataFrames as values
        
    Returns:
        Formatted string representation of the data
    """
    if not results:
        return ""
    
    formatted_data = []
    
    for file_name, df in results.items():
        # Extract the main part of the file name (remove extension and ID)
        display_name = file_name.split('_')[0]
        
        formatted_data.append(f"Table: {display_name}")
        formatted_data.append(df.to_string(index=False))
        formatted_data.append("")  # Empty line between tables
    
    return "\n".join(formatted_data)

def filter_dataframe_by_relevance(df: pd.DataFrame, query: str) -> pd.DataFrame:
    """Filter a DataFrame to include only rows and columns that are likely relevant to the query.
    
    Args:
        df: The DataFrame to filter
        query: The user's query
        
    Returns:
        Filtered DataFrame
    """
    logger.info(f"Filtering DataFrame with shape {df.shape} based on query: {query}")
    
    # Extract key terms from the query
    query_lower = query.lower()
    
    # Look for year mentions (e.g., 2022, 2021)
    year_pattern = r'\b20\d{2}\b'
    years_mentioned = re.findall(year_pattern, query)
    
    # Look for financial terms
    financial_terms = [
        "umsatz", "revenue", "sales", 
        "gewinn", "profit", "earnings", 
        "kosten", "cost", "expense",
        "verbindlichkeit", "liability",
        "personal", "staff", "employee",
        "ebit", "betriebsergebnis", "operating result",
        "jahresüberschuss", "net income", "surplus"
    ]
    
    mentioned_terms = [term for term in financial_terms if term in query_lower]
    
    # If no specific filters identified, return the original DataFrame
    if not years_mentioned and not mentioned_terms:
        logger.info("No specific filters identified, returning original DataFrame")
        return df
    
    # Create a copy to avoid modifying the original
    filtered_df = df.copy()
    
    # Filter rows by year if years are mentioned
    if years_mentioned:
        logger.info(f"Years mentioned in query: {years_mentioned}")
        # Look for columns that might contain years
        year_columns = []
        for col in filtered_df.columns:
            col_str = str(col).lower()
            if any(year in col_str for year in years_mentioned):
                year_columns.append(col)
        
        # If we found year columns, keep only those
        if year_columns:
            logger.info(f"Found year columns: {year_columns}")
            # Keep the index column(s) and the year columns
            index_cols = filtered_df.columns[:1]  # Assume first column is an index/description
            filtered_df = filtered_df[list(index_cols) + year_columns]
    
    # Filter rows by financial terms
    if mentioned_terms:
        logger.info(f"Financial terms mentioned in query: {mentioned_terms}")
        # Look for rows that contain the mentioned terms
        mask = filtered_df.apply(
            lambda row: any(term in ' '.join(row.astype(str)).lower() for term in mentioned_terms),
            axis=1
        )
        if mask.any():
            filtered_df = filtered_df[mask]
            logger.info(f"Filtered DataFrame to {filtered_df.shape[0]} rows based on financial terms")
    
    logger.info(f"Final filtered DataFrame shape: {filtered_df.shape}")
    return filtered_df

def smart_query_excel_data(financials_dir: Path, query_text: str) -> Dict[str, pd.DataFrame]:
    """Query Excel files based on the query text and filter the results for relevance.
    
    Args:
        financials_dir: Path to the financials directory
        query_text: User's question text
    
    Returns:
        dict: Dictionary with file names as keys and filtered pandas DataFrames as values
    """
    # Get the raw results first
    raw_results = query_excel_data(financials_dir, query_text)
    
    # Filter each DataFrame for relevance
    filtered_results = {}
    for file_name, df in raw_results.items():
        filtered_df = filter_dataframe_by_relevance(df, query_text)
        filtered_results[file_name] = filtered_df
    
    return filtered_results

def abbreviate_numbers_in_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Format large numbers in a DataFrame to abbreviated form (K, M, etc.).
    
    Args:
        df: The DataFrame to format
        
    Returns:
        DataFrame with abbreviated numbers
    """
    logger.info(f"Abbreviating numbers in DataFrame with shape {df.shape}")
    
    # Create a copy to avoid modifying the original
    formatted_df = df.copy()
    
    # Function to abbreviate a single number
    def abbreviate_number(value):
        try:
            # Check if the value is a number
            num = float(value)
            
            # Format based on magnitude
            if abs(num) >= 1_000_000:
                return f"{num/1_000_000:.2f}M"
            elif abs(num) >= 1_000:
                return f"{num/1_000:.1f}K"
            else:
                return value
        except (ValueError, TypeError):
            # If not a number, return as is
            return value
    
    # Apply the abbreviation to all numeric columns
    for col in formatted_df.columns:
        # Skip the first column which is usually a description
        if col == formatted_df.columns[0]:
            continue
            
        # Check if the column contains numeric data
        if pd.api.types.is_numeric_dtype(formatted_df[col]):
            formatted_df[col] = formatted_df[col].apply(abbreviate_number)
    
    logger.info("Numbers abbreviated in DataFrame")
    return formatted_df

def format_excel_data_with_abbreviations(results: Dict[str, pd.DataFrame]) -> str:
    """Format Excel data for display with abbreviated numbers.
    
    Args:
        results: Dictionary with file names as keys and pandas DataFrames as values
        
    Returns:
        Formatted string representation of the data with abbreviated numbers
    """
    if not results:
        return ""
    
    formatted_data = []
    
    for file_name, df in results.items():
        # Extract the main part of the file name (remove extension and ID)
        display_name = file_name.split('_')[0]
        
        # Abbreviate numbers in the DataFrame
        abbreviated_df = abbreviate_numbers_in_dataframe(df)
        
        formatted_data.append(f"Table: {display_name}")
        formatted_data.append(abbreviated_df.to_string(index=False))
        formatted_data.append("")  # Empty line between tables
    
    return "\n".join(formatted_data) 