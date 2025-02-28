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

logger.info(f"Vector DB path: {DB_PATH}")
logger.info(f"Financials directory: {FINANCIALS_DIR}")

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
        logger.info(f"Successfully connected to LanceDB table: {TABLE_NAME}")
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
    1. Cite the source document and page number
    2. Summarize the key insights relevant to the question
    3. IMPORTANT: If industry report data is provided in the context, use it to answer the question - don't claim you lack data if it's available
    4. If comparing company data to industry benchmarks, highlight specific differences and similarities
    
    IMPORTANT: NEVER respond with a generic message about lacking industry data if there is ANY industry report data in the context. Even if the data is limited, provide the best analysis you can with what's available.
    
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
            model="gpt-4o",
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
            }
            .search-result summary {
                cursor: pointer;
                color: #0f52ba;
                font-weight: 500;
            }
            .search-result summary:hover {
                color: #1e90ff;
            }
            .metadata {
                font-size: 0.9em;
                color: #666;
                font-style: italic;
            }
            </style>
        """,
            unsafe_allow_html=True,
        )

        # Display report data if available
        if context['report_data']:
            logger.info("Displaying report data in UI")
            st.write("Found relevant sections in industry reports:")
            for chunk in context['report_data'].split("\n\n"):
                # Split into text and metadata parts
                parts = chunk.split("\n")
                text = parts[0]
                metadata = {
                    line.split(": ")[0]: line.split(": ")[1]
                    for line in parts[1:]
                    if ": " in line
                }

                source = metadata.get("Source", "Branchenreport")  # Default to "Branchenreport" instead of "Unknown source"
                title = metadata.get("Title", "Branchenanalyse")   # Default to "Branchenanalyse" instead of "Untitled section"

                # Ensure we have meaningful display names
                if source == "Unknown":
                    source = "Branchenreport"
                
                if title == "Untitled":
                    title = "Branchenanalyse"
                
                # Create a more informative summary that includes both source and title
                summary_text = source
                if "p." in source:
                    # If the source already contains page numbers, don't add the title to avoid redundancy
                    pass
                elif title and title != "Branchenanalyse" and title not in source:
                    # Only add the title if it's meaningful and not already in the source
                    summary_text = f"{source} - {title}"

                st.markdown(
                    f"""
                    <div class="search-result">
                        <details>
                            <summary>{summary_text}</summary>
                            <div class="metadata">Quelle: {source}</div>
                            <div class="metadata">Abschnitt: {title}</div>
                            <div style="margin-top: 8px;">{text}</div>
                        </details>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
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
                                <div style="margin-top: 8px; overflow-x: auto;">
                                    <pre>{table_content}</pre>
                                </div>
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
