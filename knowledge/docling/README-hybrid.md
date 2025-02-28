# LangChain-Based Hybrid Retrieval System

This system combines structured financial data (Excel) and unstructured industry reports (vector database) using LangChain for intelligent query routing and retrieval.

## Overview

The hybrid retrieval system:

1. Uses LangChain to analyze query intent and determine which data sources to use
2. Intelligently routes queries to the appropriate data sources
3. Reformulates queries to improve retrieval quality
4. Combines results from multiple sources before passing to OpenAI for response generation

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the chat application:
   ```
   streamlit run 4-chat.py
   ```

## How It Works

### LangChain Query Router

The system uses LangChain to:
1. Analyze the user's query to determine intent
2. Identify which financial files and data are relevant
3. Decide whether to retrieve financial data, industry report data, or both
4. Reformulate the query to improve retrieval quality

### Financial Data Retrieval

When financial data is needed:
1. The system scans the Excel files in the financials directory
2. It selects relevant Excel files based on keywords in the query
3. It reads and formats the Excel data for presentation

### Industry Report Retrieval

For industry report data:
1. The system uses the reformulated query for semantic search via LanceDB
2. It retrieves the most relevant text chunks
3. It includes source information (document name, page numbers, etc.)

### Response Generation

The system:
1. Combines both data sources into a comprehensive context
2. Provides this context to OpenAI's model
3. Instructs the model to cite sources and explain the data in business terms
4. Streams the response back to the user

## Architecture

```
┌─────────────┐     ┌───────────────┐     ┌───────────────┐
│  User Query  │────▶│  LangChain    │────▶│  Excel Files  │
└─────────────┘     │  Query Router  │     └───────────────┘
                    │                │     ┌───────────────┐
                    │                │────▶│  Vector DB    │
                    └───────────────┘     └───────────────┘
                           │
                           ▼
                    ┌───────────────┐
                    │  Combined     │
                    │  Context      │
                    └───────────────┘
                           │
                           ▼
                    ┌───────────────┐
                    │  OpenAI       │
                    │  Response     │
                    └───────────────┘
```

## Data Sources

### Financial Data

The financial data is stored in Excel files and includes:
- Balance sheet information (Bilanz)
- Income statements (Gewinn- und Verlustrechnung)
- Revenue trends (Entwicklung Bruttoumsatz)
- Payment behavior (Entwicklung Zahlungsverhalten)
- Cost center analysis (Kostenstellenanalyse)
- Liquidity information (Liquidität)
- Budget vs. actual comparisons (Soll-Ist Vergleich)

### Industry Reports

The industry reports are stored as vector embeddings in LanceDB, allowing for semantic search based on the meaning of the query rather than just keywords.

## Customization

You can customize the system by:
- Adding more Excel files to the financials directory
- Adding more industry reports to the vector database
- Modifying the LangChain router prompt to improve routing decisions
- Adjusting the system prompt for the OpenAI model
- Updating the keyword-to-file mapping in excel_utils.py to improve file selection 