# Clinical Scribe AI: HCP Interaction Logger

A high-performance, AI-driven CRM module for clinical interaction tracking. Built with a focus on modularity, persistent data integrity, and autonomous agentic workflows using LangGraph and Groq.

**🌐 Live Demo:** [ai-crm-hcp.vercel.app](https://ai-crm-hcp.vercel.app)

## 🚀 Key Features

- **Conversational Logging**: Log complex interactions via a simple chat interface. The AI automatically extracts entities like HCP name, date, topics, and sentiment.
- **AI-Powered Insights**: Automatically generates "Clinical Next Steps" based on the context of your discussion using Llama 3.3 70B.
- **Real-time Synchronization**: A split-screen dashboard where the structured form updates instantly as you chat with the AI assistant.
- **Intelligent History**: Retrieve and manage historical engagement data stored in a relational database.
- **Modern UI**: A polished, responsive interface built with Tailwind CSS, featuring "Glassmorphism" cards and smooth Framer Motion animations.

## 🕹 Core Operations

1.  **Search & Populate**: Retrieve healthcare provider data and populate core engagement fields through conversational search or direct database lookups.
2.  **Clear Draft (UI Reset)**: Instantly clear the current session state and local engagement buffers to initialize a fresh clinical log.
3.  **Log a New Interaction (Data Extraction)**: Leverage agentic AI to autonomously extract entities, sentiments, and outcomes from natural language narratives.
4.  **Delete a Record (Permanent Removal)**: Securely remove historical interaction logs from the relational database via authenticated API endpoints.
5.  **Update an Existing Interaction**: Modify and synchronize previously logged engagement details using the split-screen real-time editor.

## 🛠 Technical Stack

- **Frontend**: React 18+, Redux Toolkit, Tailwind CSS, Framer Motion.
- **Backend**: Python 3.10+, FastAPI, LangGraph.
- **Database**: PostgreSQL / SQLAlchemy ORM.
- **AI Engine**: Groq API (Llama 3.3 70B for reasoning and extraction).

## 💡 Design Principles

- **No Hard Coding**: The UI state is exclusively driven by dynamic AI tool outputs.
- **Atomic Data Handling**: Full interaction context, including Next Best Action, is captured in a single-turn state transition.
- **Resilient Architecture**: Includes structured state management and exponential backoff for API reliability.

## ⚙️ Local Setup Instructions

1.  **Clone the repository**:
    ```bash
    git clone <your-repo-url>
    cd clinical-scribe-ai
    ```
2.  **Environment Configuration**:
    Create a `.env` file in the root directory:
    ```env
    GROQ_API_KEY=your_groq_api_key_here
    DATABASE_URL=your_database_url_here
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    npm install
    ```
4.  **Start the application**:
    ```bash
    npm run dev
    ```

## 🌐 Vercel Deployment

This project is optimized for deployment on **Vercel**.

1.  **Connect Repository**: Connect your GitHub/GitLab repo to Vercel.
2.  **Environment Variables**: Add your `GROQ_API_KEY` and `DATABASE_URL` in the Vercel project settings.
3.  **Build Settings**: Vercel will automatically detect the Vite build for the frontend. For the Python backend, ensure your routes are configured correctly in `vercel.json` if using a monorepo structure.

## 📡 API Documentation

### `POST /api/chat`
The primary endpoint for conversational CRM interactions.

**Request Payload:**
```json
{
  "message": "Today I met Dr. Thorne, it was positive. We discussed the new oncology study.",
  "history": [],
  "formState": { "hcpName": "", "sentiment": "", ... }
}
```

---

## ⚖️ Technical Justification: LLM-Driven Tool Calling

Unlike traditional CRM systems that rely on hard-coded state machines, this module implements a **Strictly Dynamic Agentic Flow**:
1.  **Partial Dynamic Patching**: Tools identify exactly which fields in the Redux state need mutation.
2.  **Zero-Shot Extraction**: Handles unstructured human speech without requiring specific regex patterns.
3.  **SQLAlchemy Integration**: All historical context is retrieved via standard SQL queries.
