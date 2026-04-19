import { GoogleGenerativeAI } from '@google/generative-ai';
import Flashcard from '../models/Flashcard.js';
import dotenv from 'dotenv';
dotenv.config();

// Round Robin API Key selection
const API_KEYS = [
  process.env.GEMINI_API_KEY_1 || "AIzaSyAvSR7PVcIiC-Te4QM3m4CA03s6QCQQYlY", // fallback to hardcoded from python for now
  process.env.GEMINI_API_KEY_2 || "AIzaSyDXUUFGPCH5o1c9J3acCy-9rPhwwcLMZwk",
  process.env.GEMINI_API_KEY_3 || "AIzaSyDALhj2sL22zzC1Wugw8b9eocrTEBz4AT4",
  process.env.GEMINI_API_KEY_4 || "AIzaSyD_bMJNM0PpHxVYax8m1nleK-yYl9pfRPM",
];
let apiKeyIndex = 0;

function getNextApiKey() {
  const key = API_KEYS[apiKeyIndex];
  apiKeyIndex = (apiKeyIndex + 1) % API_KEYS.length;
  return key;
}

export const extractText = async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No image provided' });
    }

    const genAI = new GoogleGenerativeAI(getNextApiKey());
    const model = genAI.getGenerativeModel({ model: "gemini-2.5-flash" }); // Using 2.5 flash

    // Convert multer buffer to format gemini needs
    const imagePart = {
      inlineData: {
        data: req.file.buffer.toString("base64"),
        mimeType: req.file.mimetype
      }
    };

    const prompt = "Extract clear readable text from this image:";
    const result = await model.generateContent([prompt, imagePart]);
    const text = result.response.text();

    res.json({ text: text.trim() });
  } catch (error) {
    console.error("OCR Error:", error);
    res.status(500).json({ error: "Failed to extract text from image." });
  }
};

export const generateFlashcards = async (req, res) => {
  try {
    const { text, numCards = 5 } = req.body;
    if (!text) {
      return res.status(400).json({ error: 'Text is required to generate flashcards.' });
    }

    let limit = parseInt(numCards);
    if (isNaN(limit) || limit < 1) limit = 5;
    if (limit > 50) limit = 50;

    const genAI = new GoogleGenerativeAI(getNextApiKey());
    const model = genAI.getGenerativeModel({ model: "gemini-2.5-flash-lite" });

    const prompt = `Create ${limit} QUESTION–ANSWER flashcards from the following text.
Return ONLY a valid JSON array (no surrounding markdown, no extra text). Example:
[
  { "q": "question 1", "a": "answer 1" },
  { "q": "question 2", "a": "answer 2" }
]

Make each question unique and ensure answers are correct.

Text:
${text}`;

    const result = await model.generateContent(prompt);
    let rawText = result.response.text().trim();
    
    // Attempt to strip json markdown if it returned it
    if (rawText.startsWith('```json')) {
      rawText = rawText.substring(7);
      if (rawText.endsWith('```')) rawText = rawText.slice(0, -3);
    } else if (rawText.startsWith('```')) {
      rawText = rawText.substring(3);
      if (rawText.endsWith('```')) rawText = rawText.slice(0, -3);
    }

    rawText = rawText.trim();
    const parsedCards = JSON.parse(rawText);

    if (!Array.isArray(parsedCards)) {
      throw new Error("Returned output is not a JSON list array");
    }

    const flashcards = parsedCards.filter(c => c.q && c.a).map(c => ({
      question: c.q.trim(),
      answer: c.a.trim(),
      sourceTextSnippet: text.substring(0, 50) + "..."
    }));

    // Optionally save to MongoDB
    try {
      await Flashcard.insertMany(flashcards);
    } catch(dbErr) {
      console.warn("Could not save flashcards to DB, returning from memory.", dbErr.message);
    }

    res.json({ flashcards });
  } catch (error) {
    console.error("Flashcard Gen Error:", error);
    res.status(500).json({ error: "Failed to generate flashcards.", details: error.message });
  }
};
