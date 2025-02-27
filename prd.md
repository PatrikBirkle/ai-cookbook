---
description: Product Requirements
globs: 
alwaysApply: false
---

1. Overview

Project Title: AI Recommendations MVP – “CFO-as-a-Service”
Stakeholder: Tax Accounting Firm (Data Platform Owner)
Goal: Demonstrate how AI can generate strategic financial recommendations using (a) industry-specific PDF reports (RAG) and (b) client financial data from Excel (stored in Supabase). MVP focuses on a “bakery” industry case.

2. User Flow
	1.	Open Website (with Dummy Data)
	•	User (Tax Advisor) navigates to a demo site pre-loaded with sample bakery financial data.
	2.	Click on “AI Recommendation” in Sidebar
	•	A prompt appears asking the user to specify the client’s industry.
	•	For the MVP demo, the user chooses “Bakery”.
	3.	Chat Interface
	•	After selecting the industry, the user is shown a chat screen.
	•	The system has already retrieved:
	1.	The bakery-focused industry reports from a vector store.
	2.	The relevant financial CSV data for this client from Supabase.
	•	The user can now pose questions (e.g., “What are the top cost-saving areas?”).
	•	The AI model responds using:
	•	RAG for industry insights (from PDF embeddings).
	•	Structured data from the client’s Excel-based financials in Supabase.
	4.	Recommendations Display
	•	The system provides high-level strategic advice referencing both industry best practices (from the PDF) and the client’s numeric data.
	•	Links/references to source passages in the PDF are optional in the chat answer.

3. Objectives & Scope
	•	Key Objectives
	1.	Showcase the combined power of retrieval from industry documents and queryable structured data.
	2.	Provide a basic chat interface that yields actionable, high-level recommendations.
	•	Scope
	1.	Industry Reports: RAG approach on ~12 PDF documents for context.
	2.	Financial Data: Ingest Excel (saved as XLSX) to Supabase; keep structured metrics accessible for queries.
	3.	Chat UI: Single conversation flow that merges textual insights + numeric data.
	4.	Minimal Production-Ready Features: Enough reliability to demonstrate how CFO-as-a-Service might look.
	•	Out of Scope
	•	Advanced compliance or real-time data pipelines.
	•	Multiple industries beyond “Bakery” for the MVP (dummy placeholders for future expansions).

4. Functional Requirements

4.1 Data Handling
	1.	Excel Ingestion to Supabase
	•	Upload the XLSX files for the “bakery” client.
	•	Parse and store relevant metrics (e.g., revenue, costs, liquidity ratios) in Supabase tables.
	2.	Industry Reports (RAG)
	•	Convert ~12 bakery-related PDF industry reports to text.
	•	Chunk and embed text; store embeddings in a vector DB (can be powered by Supabase pgvector or an external service).
	•	Retrieve top chunks at query time to feed into the AI model.

4.2 Chat & Recommendations
	1.	User Industry Selection
	•	When clicking “AI Recommendation” in the sidebar, user must select from a dropdown (“Bakery”) to load the relevant data & embeddings.
	2.	Chat Interface
	•	Display a chat box where user can type queries.
	•	System uses:
	•	RAG (embedded PDFs) for industry knowledge.
	•	Supabase data for structured financial context.
	•	Output is a short paragraph or bullet points with recommended actions, referencing both the user’s data (e.g., “Your revenue margin is X%…”) and industry best practices.
	3.	References / Citations
	•	Optionally show source references (e.g., PDF page, dataset used) within the chat response or in a collapsible “Details” section.

4.3 Dashboard Integration
	1.	Sidebar Navigation
	•	“AI Recommendation” link in the existing platform’s sidebar.
	•	Minimal styling consistent with the existing dashboard.
	2.	Integration Points
	•	Re-use existing login / session management if applicable.
	•	For MVP, a single-page “AI Recommendation” view is sufficient.

5. Non-Functional Requirements
	1.	Performance
	•	Chat responses should return in <10 seconds under typical conditions.
	2.	Usability
	•	The flow must be simple:
	•	Website → Sidebar → Select “Bakery” → Chat → Receive immediate insights.
	3.	Scalability
	•	PDFs should be easy to expand beyond the initial 12 documents.
	•	Supabase’s hosting can handle future data volume if more test clients are added.
	4.	Security
	•	Basic user authentication is enough for the MVP.
	•	Future phases may require data partitioning (per-client).

6. Technical Stack
	1.	Front-End
	•	Existing dashboard (e.g., React/Next.js or similar).
	•	New “AI Recommendation” page with a chat component.
	2.	Supabase
	•	Use Supabase as the primary store for:
	•	Client’s financial data (parsed from XLSX).
	•	Potentially for vector embeddings (if using Supabase pgvector).
	•	API or direct client library calls from the front-end to fetch data.
	3.	AI Model / RAG Logic
	•	Use a serverless function or a simple backend service:
	•	Retrieve relevant PDF chunks from vector DB (Supabase or an external vector store).
	•	Retrieve structured data from Supabase (e.g., revenue, cost).
	•	Call an LLM (e.g., OpenAI GPT API).
	•	Compose final text response, then return it to the front-end chat.

7. User Interface Requirements
	1.	Industry Selection Modal
	•	Pop-up or panel that asks: “Please select the client’s industry.”
	•	For MVP: “Bakery” is default or only option.
	2.	Chat Window
	•	Text input at bottom.
	•	Chat history above, with the system’s responses.
	•	Option to show/hide references to data sources.
	3.	Dashboard Sidebar
	•	“AI Recommendation” link that opens the new chat page.

8. Implementation Plan
	1.	Set Up Supabase
	•	Create tables for storing bakery financial data.
	•	(Optionally) set up pgvector or an external vector DB.
	2.	Embed & Ingest PDFs
	•	Convert PDFs → text → chunk → embed.
	•	Store vectors + metadata in pgvector.
	3.	Front-End Chat & Industry Picker
	•	Build a basic page with a modal for “Select Industry,” then chat interface.
	•	Integrate the “AI Recommendation” link in the sidebar.
	4.	Backend/Serverless
	•	Endpoint that handles chat requests.
	•	Retrieves user’s financial data from Supabase, relevant PDF text from vector store, calls LLM.
	5.	Testing
	•	Verify end-to-end flow: open website → pick “Bakery” → ask question → get a response referencing correct data.
	•	Evaluate recommendation quality with real sample data.
	6.	Demo
	•	Present a short live demonstration.
	•	Gather stakeholder feedback.