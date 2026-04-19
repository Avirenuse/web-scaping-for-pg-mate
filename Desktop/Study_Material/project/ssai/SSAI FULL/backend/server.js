import express from 'express';
import cors from 'cors';
import mongoose from 'mongoose';
import dotenv from 'dotenv';
import multer from 'multer';

// Import API routes/controllers early once we create them
import { extractText, generateFlashcards } from './controllers/aiController.js';
import { addDocument, searchSimilarText } from './controllers/ragController.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Setup multer for image upload memory storage
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// MongoDB Connection (Fallback to memory/dummy array if fails to allow app to run easily locally without Mongo setup)
let useMemoryFallback = false;
mongoose.connect('mongodb://localhost:27017/ssaidb')
  .then(() => console.log('✅ Connected to local MongoDB'))
  .catch((err) => {
    console.error('⚠️ MongoDB Connection Failed. Running in Memory Fallback Mode.', err.message);
    useMemoryFallback = true;
  });

// Simple root check
app.get('/', (req, res) => {
  res.json({ message: "MERN Backend is running!" });
});

// Routes
// 1. OCR Extraction (takes image file)
app.post('/api/extract-text', upload.single('image'), extractText);

// 2. Flashcard Generation (takes text)
app.post('/api/flashcards', generateFlashcards);

// 3. RAG Add Text
app.post('/api/rag/add', async (req, res) => {
  const result = await addDocument(req, res, useMemoryFallback);
  return result;
});

// 4. RAG Search Details
app.post('/api/rag/search', async (req, res) => {
  const result = await searchSimilarText(req, res, useMemoryFallback);
  return result;
});

// Start listening
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
});
