# LearnTube AI — YouTube Learning Assistant

LearnTube AI is an AI-powered learning assistant that turns YouTube videos into interactive study resources. Users can process a video, explore its transcript, ask questions about video content, and generate summaries, study notes, and quizzes.

## Features

- **YouTube transcript processing:** Fetches transcripts for learning and revision.
- **Multilingual support:** Translates transcript content into English when needed while preserving timestamps.
- **RAG-based question answering:** Uses Gemini embeddings and FAISS similarity search to retrieve relevant transcript chunks before generating answers.
- **Evidence validation:** Checks whether generated answers are supported by retrieved video context and returns a fallback response when support is insufficient.
- **AI-generated summaries:** Generates structured summaries with an overview, key points, concepts, and takeaways.
- **Study notes:** Creates structured notes from transcript sections.
- **Quizzes:** Generates multiple-choice quizzes based on video content.
- **User authentication:** Uses JWT access tokens to protect user-specific functionality.
- **Study history:** Stores study sessions, transcripts, summaries, notes, quizzes, and chat history in MongoDB.

## Technology Stack

| Component | Technologies |
|---|---|
| Frontend | React, Vite, JavaScript, Axios |
| Backend | Python, FastAPI, Uvicorn |
| Generative AI | Google Gemini API (`google-genai`) |
| Retrieval | RAG, FAISS, Gemini embeddings |
| Database | MongoDB |
| Authentication | JSON Web Tokens (JWT) |
| Testing | Pytest |

## Architecture

```text
User
 |
 v
React Frontend (Vite)
 |
 | HTTP requests with Axios
 v
FastAPI Backend
 |
 +--> YouTube Transcript Service
 |       |
 |       v
 |    Transcript Processing and Translation
 |
 +--> RAG Pipeline
 |       |
 |       +--> Text Chunking
 |       +--> Gemini Embeddings
 |       +--> FAISS Similarity Search
 |       +--> Gemini Answer Generation
 |       +--> Answer Validation
 |
 +--> Summary, Notes, and Quiz Services
 |
 +--> JWT Authentication
 |
 v
MongoDB
```

## Prerequisites

Install the following before running the project:

- Python 3.12 or later
- Node.js and npm
- MongoDB running locally or an accessible MongoDB instance
- A Google Gemini API key

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/Akshayagunda1105/LearnTube-AI.git
cd LearnTube-AI
```

### 2. Configure the backend

Open a terminal in the project root and run:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create a `.env` file inside the `backend` directory with the following variables:

```dotenv
GEMINI_API_KEY=your_gemini_api_key
JWT_SECRET_KEY=replace_with_a_long_random_secret
```

Replace the example values with your own credentials. Never commit your actual `.env` file or API keys.

The application expects MongoDB at `mongodb://127.0.0.1:27017` by default.

### 3. Start the backend

From the `backend` directory, run:

```powershell
python -m uvicorn app.main:app --reload
```

The backend API will be available at:

- API: http://127.0.0.1:8000
- Interactive API documentation: http://127.0.0.1:8000/docs

Keep this terminal running.

### 4. Start the frontend

Open a second terminal and run:

```powershell
cd C:\Users\aksha\LearnTube-AI\frontend
npm install
npm run dev
```

Open the local URL printed by Vite, usually `http://localhost:5173`.

The frontend API configuration currently targets `http://127.0.0.1:8000`, so the backend must be running locally.

## Running Tests

From the `backend` directory, activate the virtual environment and run:

```powershell
python -m pytest -q
```

The standard test suite uses automated tests and does not require enabling live RAG tests.

To run the opt-in live RAG pipeline and retrieval tests, configure the required API key and run:

```powershell
$env:RUN_REAL_RAG_TEST="1"
python -m pytest -v test_real_rag_pipeline.py test_rag_retrieval.py
Remove-Item Env:RUN_REAL_RAG_TEST
```

Live tests may make external API calls and take longer than the standard test suite.

## Project Structure

```text
LearnTube-AI/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── services/
│   │   └── database/
│   ├── requirements.txt
│   └── tests and test files
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
├── .gitignore
└── README.md
```

## Current Limitations

- The frontend is configured for local backend access.
- MongoDB must be available for database-dependent features.
- Gemini API access is required for AI-powered features.
- Answer validation reduces unsupported responses but does not guarantee that every answer is correct.
- Production deployment and production environment configuration are not included in the local setup instructions.

## Future Improvements

- Deploy the frontend and backend to production hosting.
- Configure environment-specific API URLs and deployment settings.
- Expand evaluation of retrieval relevance and answer faithfulness.
- Add further integration and end-to-end tests.

## Author

**Akshaya Gunda**

GitHub: https://github.com/Akshayagunda1105
