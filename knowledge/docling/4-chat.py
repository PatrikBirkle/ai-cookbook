import streamlit as st
import lancedb
import pandas as pd
import re
import logging
import sys
import json
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from utils.langchain_router import create_query_router, process_query
from utils.vector_search import get_vector_search_function
from typing import Optional
import os
import hashlib
import base64
from PyPDF2 import PdfReader
import io

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Log to stdout (terminal)
        logging.FileHandler('hybrid_retrieval.log')  # Also save logs to a file
    ]
)
logger = logging.getLogger('hybrid_retrieval')

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

# Initialize OpenAI client
client = OpenAI()
logger.info("OpenAI client initialized")

# Constants
DB_PATH = Path(__file__).parent.parent.parent / "data/lancedb"  # Go up three levels to reach root
TABLE_NAME = "docling"
FINANCIALS_DIR = Path(__file__).parent.parent.parent / "financials"  # Path to financials directory
REPORTS_DIR = Path(__file__).parent.parent.parent / "reports"  # Path to original PDF reports

logger.info(f"Vector DB path: {DB_PATH}")
logger.info(f"Financials directory: {FINANCIALS_DIR}")
logger.info(f"Reports directory: {REPORTS_DIR}")

# Initialize LanceDB connection
@st.cache_resource
def init_db():
    """Initialize database connection.

    Returns:
        LanceDB table object
    """
    logger.info(f"Initializing LanceDB connection to {DB_PATH}")
    try:
        db = lancedb.connect(str(DB_PATH))  # Convert Path to string for lancedb
        table = db.open_table(TABLE_NAME)
        row_count = table.count_rows()
        logger.info(f"Successfully connected to LanceDB table: {TABLE_NAME} with {row_count} total chunks")
        return table
    except Exception as e:
        logger.error(f"Error connecting to LanceDB: {e}", exc_info=True)
        st.error(f"Failed to connect to vector database: {e}")
        return None

# Initialize LangChain router
@st.cache_resource
def init_router():
    """Initialize the LangChain query router.
    
    Returns:
        LangChain router chain
    """
    logger.info("Initializing LangChain query router")
    try:
        router = create_query_router()
        logger.info("LangChain router initialized successfully")
        return router
    except Exception as e:
        logger.error(f"Error initializing LangChain router: {e}", exc_info=True)
        st.error(f"Failed to initialize query router: {e}")
        return None


def get_context(query: str, table, num_results: int = 3, include_reports: Optional[bool] = None) -> dict:
    """Search the database for relevant context using LangChain router.

    Args:
        query: User's question
        table: LanceDB table object
        num_results: Number of results to return
        include_reports: If provided, overrides the router's decision on whether to include industry report data

    Returns:
        dict: Context from relevant sources
    """
    logger.info(f"Getting context for query: {query}")
    if include_reports is not None:
        logger.info(f"Include reports setting (override): {include_reports}")
    else:
        logger.info("Using router to determine whether to include reports")
    
    # Initialize the router
    router = init_router()
    if not router:
        logger.error("Failed to initialize router, cannot get context")
        return {'financial_data': '', 'report_data': ''}
    
    # Check if this is a comparison query to determine how many results to return
    query_lower = query.lower()
    comparison_keywords = ["vergleich", "comparison", "benchmark", "durchschnitt", "average", 
                          "typical", "standard", "norm", "branche", "industry"]
    is_comparison_query = any(keyword in query_lower for keyword in comparison_keywords)
    
    # Use more results for comparison queries
    actual_num_results = 5 if is_comparison_query else num_results
    if is_comparison_query:
        logger.info(f"Comparison query detected, increasing number of results to {actual_num_results}")
    
    # Create a vector search function
    vector_search_func = get_vector_search_function(DB_PATH, TABLE_NAME, actual_num_results)
    
    # Process the query using the router
    try:
        # Pass the include_reports parameter to control whether to include industry report data
        context = process_query(query, router, FINANCIALS_DIR, vector_search_func, force_report_data=include_reports)
        
        # Log the number of chunks in the report data
        if context['report_data']:
            chunks = context['report_data'].split("\n\n")
            logger.info(f"Vector search returned {len(chunks)} chunks")
        
        logger.info(f"Context retrieved - Financial data: {len(context['financial_data'])} chars, Report data: {len(context['report_data'])} chars")
        return context
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        return {'financial_data': '', 'report_data': ''}


def get_chat_response(messages, context: dict) -> str:
    """Get streaming response from OpenAI API.

    Args:
        messages: Chat history
        context: Retrieved context from databases

    Returns:
        str: Model's response
    """
    logger.info("Generating chat response from OpenAI")
    
    # Combine context from different sources
    combined_context = ""
    
    # Function to truncate context if it's too large
    def truncate_context(text, max_chars=4000):
        if len(text) > max_chars:
            logger.warning(f"Truncating context from {len(text)} to {max_chars} characters")
            return text[:max_chars] + "... [truncated due to length]"
        return text
    
    if context['report_data']:
        report_data = truncate_context(context['report_data'])
        # Add a clear marker that this is industry report data
        combined_context += f"INDUSTRY REPORT DATA (Use this for industry comparisons and benchmarks):\n{report_data}\n\n"
        logger.info("Including industry report data in context")
    
    if context['financial_data']:
        financial_data = truncate_context(context['financial_data'])
        combined_context += f"FINANCIAL DATA (Company specific information):\n{financial_data}\n\n"
        logger.info("Including financial data in context")
    
    if not combined_context:
        logger.warning("No context data available for the query")
        combined_context = "No specific financial data or industry reports are available for this query. Please provide a more specific question or check if the database contains the relevant information."
    
    system_prompt = f"""You are an expert financial analyst for bakeries. You have access to financial data and industry reports.
    Your task is to answer questions about the financial data of the company and industry reports.
    
    When answering questions about financial data:
    1. Cite the specific table you're referencing
    2. Mention specific numbers and trends from the data
    3. Explain what the data means in easy terms
    4. If the user asks about a specific year, make sure to include the year in the response.
    5. IMPORTANT: Always abbreviate large numbers to millions (M), thousands (K), etc. For example, convert 6,222,255 € to 6.22M €, 2,968,433 € to 2.97M €, etc.
    
    When answering questions about industry reports:
    1. IMPORTANT: Always cite the specific source code when referencing industry data
    2. Mention the exact source document and page number if available
    3. Summarize the key insights relevant to the question
    4. IMPORTANT: If industry report data is provided in the context, use it to answer the question - don't claim you lack data if it's available
    5. If comparing company data to industry benchmarks, highlight specific differences and similarities
    
    IMPORTANT: NEVER respond with a generic message about lacking industry data if there is ANY industry report data in the context. Even if the data is limited, provide the best analysis you can with what's available.
    
    When citing sources, use the exact source codes provided in the context (like "GK051" or other specific identifiers). This helps establish credibility.
    
    If absolutely no context data is available (both financial and industry report data are empty), only then should you politely explain that you don't have the specific information requested and suggest what kind of information the user could ask about instead.
    
    Context:
    {combined_context}
    """

    messages_with_context = [{"role": "system", "content": system_prompt}, *messages]
    
    logger.info(f"Sending {len(messages_with_context)} messages to OpenAI")
    logger.debug(f"System prompt length: {len(system_prompt)} characters")
    
    try:
        # Create the streaming response
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_with_context,
            temperature=0.7,
            max_tokens=1000,
            stream=True,
        )
        
        logger.info("Streaming response from OpenAI")
        
        # Use Streamlit's built-in streaming capability
        response = st.write_stream(stream)
        logger.info("Response generation complete")
        return response
    except Exception as e:
        logger.error(f"Error getting chat response from OpenAI: {e}", exc_info=True)
        st.error(f"Error generating response: {e}")
        return "I'm sorry, I encountered an error while generating a response."


# Initialize Streamlit app
st.title("📚 Financial & Industry Q&A")
st.markdown("""
This hybrid retrieval system combines financial data (Excel) and industry reports (vector database) 
to provide comprehensive answers to your questions. Ask about finances, industry trends, or both!
""")

logger.info("Streamlit app initialized")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    logger.info("Initialized empty chat history")

# Initialize database connections
table = init_db()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about finances or industry reports"):
    logger.info(f"Received user query: {prompt}")
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get relevant context
    with st.status("Searching for information...", expanded=False) as status:
        logger.info("Starting context retrieval")
        # Let the router decide whether to include reports based on the query
        context = get_context(prompt, table, include_reports=None)
        logger.info("Context retrieval complete")
        
        st.markdown(
            """
            <style>
            .search-result {
                margin: 10px 0;
                padding: 10px;
                border-radius: 4px;
                background-color: #f0f2f6;
                border: 1px solid #ddd;
            }
            .search-result summary {
                cursor: pointer;
                color: #0f52ba;
                font-weight: 500;
                padding: 5px 0;
            }
            .search-result summary:hover {
                color: #1e90ff;
            }
            .metadata {
                font-size: 0.9em;
                color: #666;
                font-style: italic;
                margin-bottom: 5px;
            }
            .pdf-viewer {
                margin: 15px 0;
                padding: 10px;
                border-radius: 4px;
                background-color: #fff;
                border: 1px solid #ddd;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .pdf-page-button {
                margin-right: 5px;
                margin-bottom: 5px;
            }
            iframe {
                border: none;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }
            </style>
        """,
            unsafe_allow_html=True,
        )

        # Display report data if available
        if context['report_data']:
            logger.info("Displaying report data in UI")
            st.write("Found relevant sections in industry reports:")
            
            # Split the report data into chunks
            chunks = context['report_data'].split("\n\n")
            
            # Show all sources
            total_sources = len(chunks)
            logger.info(f"Displaying all {total_sources} sources")
            
            # Process each chunk as an individual source
            for chunk in chunks:
                # Skip empty chunks
                if not chunk.strip():
                    continue
                
                # Log the raw chunk for debugging
                logger.info(f"Raw chunk: {chunk[:100]}...")  # Log first 100 chars
                
                # Split into text and metadata parts
                parts = chunk.split("\n")
                
                # Find where the metadata starts (lines starting with "Source:" or "Title:")
                metadata_start_idx = None
                for i, line in enumerate(parts):
                    if line.startswith("Source:") or line.startswith("Title:"):
                        metadata_start_idx = i
                        break
                
                # If no metadata markers found, use the whole chunk as text
                if metadata_start_idx is None:
                    text = chunk
                    metadata = {}
                else:
                    # Text is everything before metadata
                    text = "\n".join(parts[:metadata_start_idx])
                    # Metadata is everything after
                    metadata = {
                        line.split(": ")[0]: line.split(": ")[1]
                        for line in parts[metadata_start_idx:]
                        if ": " in line
                    }
                
                # Extract source and title
                source = metadata.get("Source", "Unknown source")
                title = metadata.get("Title", "Untitled section")
                
                # Log the original source for debugging
                logger.info(f"Original source: {source}, title: {title}")
                
                # Extract page numbers if available
                page_numbers = []
                if "page_numbers" in metadata and metadata["page_numbers"]:
                    if isinstance(metadata["page_numbers"], list):
                        page_numbers = metadata["page_numbers"]
                    elif isinstance(metadata["page_numbers"], str):
                        # Handle case where page numbers might be stored as a string
                        try:
                            page_numbers = json.loads(metadata["page_numbers"])
                        except:
                            # If it's a comma-separated string
                            page_numbers = [p.strip() for p in metadata["page_numbers"].split(',')]
                
                # Format page numbers for display
                page_info = ""
                if page_numbers:
                    if len(page_numbers) == 1:
                        page_info = f" (Seite {page_numbers[0]})"
                    else:
                        page_info = f" (Seiten {', '.join(str(p) for p in page_numbers)})"
                
                # Get the filename from metadata if available
                filename = None
                
                # First check if we have a filename in metadata
                if "filename" in metadata and metadata["filename"]:
                    filename = metadata["filename"]
                    # Format the filename to be more readable
                    formatted_name = filename.replace('_', ' ').replace('-', ' ')
                    # Replace URL-encoded characters
                    formatted_name = formatted_name.replace('%20', ' ')
                    # Capitalize words for better readability
                    formatted_name = ' '.join(word.capitalize() for word in formatted_name.split())
                    source = formatted_name
                    logger.info(f"Using filename from metadata: {filename}")
                # If source is a GK code or Quelle, try to extract from text
                elif re.match(r'GK\d+', source) or source == "Quelle" or source == "Unknown source":
                    # Look for source information in the text as fallback
                    source_match = re.search(r'\(Quelle: ([^)]+)\)', text)
                    if source_match:
                        extracted_source = source_match.group(1).strip()
                        logger.info(f"Extracted source from text: {extracted_source}")
                        source = extracted_source
                        
                        # Try to find a matching PDF file for this source
                        for file in REPORTS_DIR.glob("*.pdf"):
                            clean_source = re.sub(r'[^a-zA-Z0-9]', '', extracted_source.lower())
                            clean_file = re.sub(r'[^a-zA-Z0-9]', '', file.stem.lower())
                            
                            if clean_source in clean_file or clean_file in clean_source:
                                filename = file.stem
                                logger.info(f"Found matching PDF file for source: {filename}")
                                break
                
                # If we still don't have a filename but have a source code like "610074810 Baeckereien Inhalt"
                if not filename and "Baeckereien" in source:
                    # Try to find a matching PDF file for bakeries
                    for file in REPORTS_DIR.glob("*.pdf"):
                        if "baeck" in file.stem.lower() or "back" in file.stem.lower():
                            filename = file.stem
                            logger.info(f"Found bakery PDF file: {filename}")
                            break
                
                # Log all PDF files in the reports directory for debugging
                logger.info("Available PDF files in reports directory:")
                for file in REPORTS_DIR.glob("*.pdf"):
                    logger.info(f"  - {file.stem}")
                
                # Display the source with text and PDF buttons if available
                st.markdown(
                    f"""
                    <div class="search-result">
                        <details>
                            <summary>{source}{page_info}</summary>
                            <div class="metadata">
                                <div>Section: {title}</div>
                                {f'<div style="margin-top: 3px;"><strong>PDF Pages:</strong> {", ".join(str(p) for p in page_numbers)}</div>' if page_numbers else ''}
                            </div>
                            <div style="margin-top: 8px;">{text}</div>
                        </details>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
                
                # Add buttons to view PDF pages if we have page numbers
                if page_numbers:
                    # If we don't have a filename but have page numbers, use a default filename
                    if not filename and "Baeckereien" in source:
                        filename = "610074810_Baeckereien_Inhalt"
                        logger.info(f"Using default filename for bakery source: {filename}")
                    
                    if filename:
                        st.markdown("<div style='margin-top: 10px;'><strong>View PDF Pages:</strong></div>", unsafe_allow_html=True)
                        
                        # Create a button for each page
                        button_cols = st.columns(min(len(page_numbers), 5))  # Show up to 5 buttons per row
                        for i, page in enumerate(page_numbers):
                            col_idx = i % 5
                            with button_cols[col_idx]:
                                button_key = f"{filename}_{page}_{i}"
                                if st.button(f"📄 Page {page}", key=button_key, use_container_width=True):
                                    # Extract and display the PDF page
                                    pdf_base64 = extract_pdf_page(filename, page)
                                    if pdf_base64:
                                        st.session_state[f"show_pdf_{filename}_{page}"] = pdf_base64
                                        # Store the current page to highlight the active button
                                        st.session_state["active_pdf_page"] = page
                                        st.session_state["active_pdf_file"] = filename
                                    else:
                                        st.error(f"Could not load PDF page {page} from {filename}")
                        
                        # Display the PDF if a button was clicked
                        for page in page_numbers:
                            pdf_key = f"show_pdf_{filename}_{page}"
                            if pdf_key in st.session_state and st.session_state[pdf_key]:
                                st.markdown(f"<div style='margin-top: 15px; padding: 5px; background-color: #f0f7fb; border-left: 5px solid #0f52ba;'><strong>📑 Showing PDF:</strong> {filename}, Page {page}</div>", unsafe_allow_html=True)
                                display_pdf_page(st.session_state[pdf_key])
                                if st.button("✖️ Close PDF", key=f"close_{filename}_{page}", type="primary"):
                                    del st.session_state[pdf_key]
                                    if "active_pdf_page" in st.session_state:
                                        del st.session_state["active_pdf_page"]
                                    if "active_pdf_file" in st.session_state:
                                        del st.session_state["active_pdf_file"]
                                st.divider()
        else:
            logger.info("No report data to display")
        
        # Display financial data if available
        if context['financial_data']:
            logger.info("Displaying financial data in UI")
            st.write("Found relevant financial data:")
            for table_data in context['financial_data'].split("\n\n"):
                if table_data.strip():
                    # Extract table name
                    table_name = "Financial Data"
                    if table_data.startswith("Table:"):
                        table_name = table_data.split("\n")[0]
                        table_content = "\n".join(table_data.split("\n")[1:])
                    else:
                        table_content = table_data
                    
                    st.markdown(
                        f"""
                        <div class="search-result">
                            <details>
                                <summary>{table_name}</summary>
                                <div class="metadata">
                                    <div>Section: Financial Information</div>
                                </div>
                                <div style="margin-top: 8px;">{table_content}</div>
                            </details>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )
        else:
            logger.info("No financial data to display")

    # Display assistant response first
    with st.chat_message("assistant"):
        logger.info("Generating assistant response")
        # Get model response with streaming
        response = get_chat_response(st.session_state.messages, context)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    logger.info("Chat interaction complete")