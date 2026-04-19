# Study Buddy

An intelligent, interactive companion app that automatically generates flashcards and enables immersive Q&A (RAG) over your study materials using Google's powerful Gemini Large Language Models.

## Features
- **Upload & Read Everything**: Upload standard images or PDFs. Study Buddy parses text instantaneously.
- **Auto-Generate Flashcards**: Utilizing Gemini, Study Buddy reads your content and formulates high-yield QA flashcards to test your knowledge.
- **RAG (Retrieval-Augmented Generation)**: Uses a FAISS Vector store to instantly search and retrieve the most relevant snippets from your study document.
- **3D Immersive UI**: Fully reimagined with CSS3 3D transforms, glassmorphism, floating volumetric shadows, and parallax hovering for a deep, modern study experience.

## Tech Stack
- **Frontend**: React + Vanilla CSS (Immersive 3D styling)
- **Backend**: Flask
- **AI Models**: Google GenAI (`gemini-2.0-flash` & `gemini-2.5-flash-lite`)
- **Vector Search**: Sentence-Transformers + FAISS

## Setup Instructions

1. **Clone the repository**
2. **Environment Setup**
   Copy `.env.example` to `.env` and enter your Gemini API Keys (comma-separated if defining multiple):
   ```
   GEMINI_API_KEYS=your_first_key,your_second_key
   ```
3. **Backend** (Python)
   ```bash
   pip install -r requirements.txt
   python app.py
   ```
4. **Frontend** (React)
   In a new terminal:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
