# ---------------------------
# FULL APP: RAG + OCR (Gemini) + FLASHCARDS (Gemini)
# ---------------------------

from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from PIL import Image
import google.generativeai as genai
import faiss
import numpy as np
import json
import logging
import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------
# CONFIG
# ---------------------------
# Multiple API keys for round-robin distribution
api_keys_env = os.environ.get("GEMINI_API_KEYS", "")
API_KEYS = [k.strip() for k in api_keys_env.split(",") if k.strip()]

if not API_KEYS:
    logging.warning("No API keys found. Please set GEMINI_API_KEYS in .env")
    API_KEYS = ["DUMMY_KEY_TO_AVOID_CRASH"]

# Round-robin counter for API key rotation
api_key_index = 0


def get_next_api_key():
    """Get the next API key in round-robin fashion."""
    global api_key_index
    key = API_KEYS[api_key_index]
    api_key_index = (api_key_index + 1) % len(API_KEYS)
    return key


# Configure with the first API key initially
genai.configure(api_key=API_KEYS[0])

app = Flask(__name__)
CORS(app)

# ---------------------------
# LOAD RAG MODEL + CREATE FAISS INDEX
# ---------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")
# get embedding dimension from model to avoid hardcoding
try:
    dim = model.get_sentence_embedding_dimension()
except Exception:
    # fallback to 384 which is correct for all-MiniLM-L6-v2
    dim = 384

index = faiss.IndexFlatL2(dim)
corpus = []


# ensure index is empty and ready
# faiss IndexFlatL2 is fine to use empty, but keep corpus in sync
def add_to_rag(text):
    """Add a document to the in-memory corpus and FAISS index."""
    if not text:
        return
    corpus.append(text)
    emb = model.encode([text])
    arr = np.array(emb, dtype=np.float32)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    index.add(arr)


def rag_search(query, k=3):
    """Return up to k nearest documents for query (handles empty corpus)."""
    if len(corpus) == 0:
        return []
    q_emb = model.encode([query])
    q_arr = np.array(q_emb, dtype=np.float32)
    if q_arr.ndim == 1:
        q_arr = q_arr.reshape(1, -1)
    # ensure k does not exceed corpus size
    k = min(int(k), len(corpus))
    D, I = index.search(q_arr, k)
    results = []
    for idx in I[0]:
        if idx >= 0 and idx < len(corpus):
            results.append(corpus[idx])
    return results


# ---------------------------
# OCR USING GEMINI
# ---------------------------


def extract_text_from_file(uploaded_file):
    """Use Gemini model to extract readable text from an uploaded document (image or PDF)."""
    file_bytes = uploaded_file.read()
    uploaded_file.seek(0)
    
    mime_type = getattr(uploaded_file, "mimetype", None) or getattr(uploaded_file, "content_type", None) or "application/octet-stream"

    # Use round-robin API key selection
    api_key = get_next_api_key()
    genai.configure(api_key=api_key)

    model_g = genai.GenerativeModel("gemini-2.0-flash")
    
    part = {
        "mime_type": mime_type,
        "data": file_bytes
    }
    
    try:
        response = model_g.generate_content(
            ["Extract clear readable text from this document/image:", part]
        )
        text = getattr(response, "text", None) or (
            response[0].text
            if isinstance(response, (list, tuple)) and len(response) > 0
            else ""
        )
        return text.strip()
    except Exception as e:
        logging.exception("OCR/Extraction failed")
        raise RuntimeError(f"OCR/Extraction failed: {e}")


# ---------------------------
# FLASHCARD GENERATOR
# ---------------------------


def generate_flashcards(text, num_cards=8):
    """Generate flashcards with custom count and validation and return list of dicts."""
    # Use round-robin API key selection
    api_key = get_next_api_key()
    genai.configure(api_key=api_key)

    model_g = genai.GenerativeModel("gemini-2.5-flash-lite")

    # Validate number of cards
    try:
        num_cards = int(num_cards)
    except (ValueError, TypeError):
        num_cards = 8  # Default to 8 if invalid

    # Enforce limits: Between 1 and 50
    if num_cards < 1:
        num_cards = 1
    elif num_cards > 50:
        num_cards = 50

    prompt = f"""Create {num_cards} QUESTION–ANSWER flashcards from the following text.
Return ONLY a valid JSON array (no surrounding markdown, no extra text). Example:
[
  {{ "question": "question 1", "answer": "answer 1" }},
  {{ "question": "question 2", "answer": "answer 2" }}
]

Make each question unique and ensure answers are correct.

Text:
{text}
"""
    try:
        response = model_g.generate_content(prompt)
        raw = getattr(response, "text", None) or (
            response[0].text
            if isinstance(response, (list, tuple)) and len(response) > 0
            else ""
        )
        json_text = raw.strip()
        # strip possible markdown code fences
        if "```json" in json_text:
            json_text = json_text.split("```json", 1)[1].rsplit("```", 1)[0]
        elif "```" in json_text:
            json_text = json_text.split("```", 1)[1].rsplit("```", 1)[0]
        json_text = json_text.strip()
        flashcards = json.loads(json_text)
        if not isinstance(flashcards, list):
            logging.warning("Flashcards JSON is not a list")
            return []
        # normalize cards: ensure dicts with q and a
        valid_cards = []
        for item in flashcards:
            if isinstance(item, dict) and "question" in item and "answer" in item:
                valid_cards.append(
                    {"question": str(item["question"]).strip(), "answer": str(item["answer"]).strip()}
                )
        # If generator returned fewer cards, don't crash; return what's valid
        return valid_cards
    except json.JSONDecodeError as e:
        logging.exception("Failed to parse flashcards JSON")
        return []
    except Exception as e:
        logging.exception("Flashcard generation error")
        return []


# Store flashcards globally so they persist between requests
stored_flashcards = []


# ---------------------------
# API ROUTES
# ---------------------------
@app.route("/api/extract-text", methods=["POST"])
def api_extract_text():
    uploaded_file = request.files.get("image") or request.files.get("file")
    if uploaded_file and uploaded_file.filename:
        try:
            extracted_text = extract_text_from_file(uploaded_file)
            return jsonify({"text": extracted_text})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "No file uploaded"}), 400

@app.route("/api/rag/add", methods=["POST"])
def api_rag_add():
    data = request.get_json() or {}
    text = data.get("text", "")
    if text:
        add_to_rag(text)
        return jsonify({"success": True})
    return jsonify({"error": "No text provided"}), 400

@app.route("/api/rag/search", methods=["POST"])
def api_rag_search():
    data = request.get_json() or {}
    query = data.get("query", "")
    k = data.get("k", 3)
    if query:
        results = rag_search(query, k=k)
        return jsonify({"results": results})
    return jsonify({"error": "No query provided"}), 400

@app.route("/api/flashcards", methods=["POST"])
def api_flashcards():
    data = request.get_json() or {}
    text = data.get("text", "")
    num_cards = data.get("numCards", 12)
    if text:
        cards = generate_flashcards(text, num_cards)
        return jsonify({"flashcards": cards})
    return jsonify({"error": "No text provided"}), 400


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    app.run(debug=True, port=5000)
