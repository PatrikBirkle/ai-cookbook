"""
LangChain-based query router for hybrid retrieval system.
"""

from typing import Dict, List, Any, Optional
import pandas as pd
from pathlib import Path
import os
import json
import logging

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnablePassthrough

# Import the Excel utilities
from .excel_utils import query_excel_data, format_excel_data, smart_query_excel_data, format_excel_data_with_abbreviations

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('hybrid_retrieval')

# Define the schema for the router output
class RouterOutput(BaseModel):
    """Output schema for the query router."""
    financial_data_needed: bool = Field(description="Whether financial data is needed to answer the query")
    report_data_needed: bool = Field(description="Whether industry report data is needed to answer the query")
    financial_tables: List[str] = Field(description="List of financial tables that might be relevant", default=[])
    financial_columns: List[str] = Field(description="List of financial columns that might be relevant", default=[])
    query_type: str = Field(description="Type of query: financial, industry, or hybrid")
    reformulated_query: str = Field(description="Reformulated query for better retrieval")

def create_query_router(model_name: str = "gpt-4o-mini") -> Any:
    """Create a LangChain-based query router.
    
    Args:
        model_name: Name of the OpenAI model to use
        
    Returns:
        LangChain router chain
    """
    # Check if OpenAI API key is set
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError(
            "The OPENAI_API_KEY environment variable is not set. "
            "Please set it or pass api_key directly to the ChatOpenAI constructor."
        )
    
    # Create the LLM
    llm = ChatOpenAI(model=model_name, temperature=0)
    
    # Create the router prompt
    router_prompt = ChatPromptTemplate.from_template("""
    You are a query router for a hybrid retrieval system that can access both financial data (Excel files) 
    and industry reports (vector database).
    
    Financial data files include:
    - Bilanz: Contains balance sheet information
    - Gewinn- und Verlustrechnung: Contains income statement data
    - Liquidität: Contains liquidity information
    - Entwicklung Bruttoumsatz: Contains revenue/sales data
    - Entwicklung Zahlungsverhalten: Contains payment behavior data
    - Kostenstellenanalyse: Contains cost center analysis data
    - Soll-Ist Vergleich: Contains budget vs actual comparison data
    
    Industry reports contain unstructured text about industry trends, market analysis, etc.
    
    Based on the user's query, determine:
    1. Whether financial data is needed
    2. Whether industry report data is needed
    3. Which financial files might be relevant
    4. Which financial columns might be relevant
    5. The type of query (financial, industry, or hybrid)
    6. A reformulated query that would improve retrieval
    
    IMPORTANT: Only set report_data_needed to true if the query EXPLICITLY asks for industry information, market trends, or comparisons with industry standards using words like "industry", "market", "trend", "competitor", "comparison", "benchmark", or "sector".
    
    If the query is only about the company's financial data, set report_data_needed to false and query_type to "financial".
    
    User query: {query}
    
    Provide your response in JSON format with these exact field names:
    - financial_data_needed (boolean)
    - report_data_needed (boolean)
    - financial_tables (array of strings)
    - financial_columns (array of strings)
    - query_type (string: "financial", "industry", or "hybrid")
    - reformulated_query (string)
    """)
    
    # Create the output parser
    output_parser = JsonOutputParser(pydantic_object=RouterOutput)
    
    # Create the router chain
    router_chain = router_prompt | llm | output_parser
    
    return router_chain

def process_query(query: str, router_chain: Any, financials_dir: Path, vector_search_func: Any, force_report_data: Optional[bool] = None) -> Dict[str, str]:
    """Process a query using the router and retrieve data from appropriate sources.
    
    Args:
        query: User's query
        router_chain: LangChain router chain
        financials_dir: Path to the financials directory
        vector_search_func: Function to search the vector database
        force_report_data: If provided, overrides the router's decision on whether to include report data
        
    Returns:
        Dict with keys 'financial_data' and 'report_data'
    """
    logger.info(f"Processing query: {query}")
    
    # Route the query
    logger.info("Routing query through LangChain router")
    router_output = router_chain.invoke({"query": query})
    logger.info(f"Router output: {json.dumps(router_output, default=str, indent=2)}")
    
    context = {
        'financial_data': '',
        'report_data': '',
    }
    
    # Get financial data if needed
    if router_output.get("financial_data_needed", False):
        logger.info("Financial data needed, querying Excel files with smart filtering")
        # Use the smart query function instead of the basic one
        financial_results = smart_query_excel_data(financials_dir, query)
        # Use the new formatting function with abbreviations
        context['financial_data'] = format_excel_data_with_abbreviations(financial_results)
        logger.info(f"Financial data retrieved: {len(context['financial_data'])} characters")
        logger.debug(f"Financial data content: {context['financial_data']}")
    else:
        logger.info("Financial data not needed for this query")
    
    # Determine if report data is needed
    # If force_report_data is None, use the router's decision
    # If force_report_data is not None, use that value
    report_data_needed = force_report_data
    
    # If force_report_data is None, use the router's decision
    if report_data_needed is None:
        # Check if the query explicitly mentions industry reports, trends, or comparisons
        report_keywords = ["industry", "market", "trend", "competitor", "comparison", "benchmark", "sector", "report", 
                          "branche", "vergleich", "durchschnitt", "markt", "wettbewerb", "standard", "typisch", "normal", "üblich"]
        query_lower = query.lower()
        explicit_report_request = any(keyword in query_lower for keyword in report_keywords)
        
        # Use the router's decision, but be more aggressive in including report data
        router_says_needed = router_output.get("report_data_needed", False) or router_output.get("industry_report_data_needed", False)
        
        # Include reports if either the router says they're needed OR the query explicitly mentions reports/comparisons
        report_data_needed = router_says_needed or explicit_report_request
        
        # If the query is asking for a comparison or mentions industry benchmarks, always include report data
        comparison_keywords = ["vergleich", "comparison", "benchmark", "durchschnitt", "average", "typical", "standard", "norm"]
        is_comparison_query = any(keyword in query_lower for keyword in comparison_keywords)
        if is_comparison_query:
            report_data_needed = True
            logger.info("Query appears to be asking for comparison/benchmarks, forcing inclusion of report data")
    
    logger.info(f"Report data needed: {report_data_needed}")
    
    # Get report data if needed
    if report_data_needed:
        logger.info("Report data needed, querying vector database")
        reformulated_query = router_output.get("reformulated_query", query)
        logger.info(f"Reformulated query for vector search: {reformulated_query}")
        
        report_results = vector_search_func(reformulated_query)
        
        if report_results:
            # The vector search function already returns a string with sources separated by "\n\n"
            context['report_data'] = report_results
            logger.info(f"Report data retrieved: {len(context['report_data'])} characters")
            logger.debug(f"Report data content: {context['report_data']}")
        else:
            logger.warning("No report data found")
    else:
        logger.info("Report data not needed for this query")
    
    return context 