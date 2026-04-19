import { GoogleGenerativeAI } from '@google/generative-ai';
import Document from '../models/Document.js';
import dotenv from 'dotenv';
dotenv.config();

let memoryCorpus = []; // Fallback array if DB is not connected

const getGenAI = () => {
    // using the first key for embeddings
    const key = process.env.GEMINI_API_KEY_1 || "AIzaSyAvSR7PVcIiC-Te4QM3m4CA03s6QCQQYlY";
    return new GoogleGenerativeAI(key);
}

const generateEmbedding = async (text) => {
    const genAI = getGenAI();
    const model = genAI.getGenerativeModel({ model: "text-embedding-004"});
    const result = await model.embedContent(text);
    return result.embedding.values;
}

// Cosine similarity utility
function cosineSimilarity(A, B) {
    let dotProduct = 0;
    let normA = 0;
    let normB = 0;
    for (let i = 0; i < A.length; i++) {
        dotProduct += A[i] * B[i];
        normA += A[i] * A[i];
        normB += B[i] * B[i];
    }
    if (normA === 0 || normB === 0) return 0;
    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

export const addDocument = async (req, res, useMemoryFallback = false) => {
    try {
        const { text } = req.body;
        if (!text) {
            return res.status(400).json({ error: "Text is required" });
        }

        const embedding = await generateEmbedding(text);

        if (useMemoryFallback) {
            memoryCorpus.push({ text, embedding });
            return res.json({ message: "Document added to memory vector store", success: true });
        } else {
            const doc = new Document({ text, embedding });
            await doc.save();
            return res.json({ message: "Document saved to MongoDB", success: true });
        }

    } catch (error) {
        console.error("RAG Add Error", error);
        res.status(500).json({ error: "Failed to add document to vector store" });
    }
}

export const searchSimilarText = async (req, res, useMemoryFallback = false) => {
    try {
        const { query, k = 3 } = req.body;
        if (!query) {
            return res.status(400).json({ error: "Query is required" });
        }

        const queryEmbedding = await generateEmbedding(query);
        let allDocs = [];

        if (useMemoryFallback) {
            allDocs = memoryCorpus;
        } else {
            allDocs = await Document.find({});
        }

        if (allDocs.length === 0) {
            return res.json({ results: [] });
        }

        // Calculate cosine similarity manually vs all docs
        const scoredDocs = allDocs.map(doc => {
            const score = cosineSimilarity(queryEmbedding, doc.embedding);
            return { text: doc.text, score };
        });

        // Sort descending and take top K
        scoredDocs.sort((a, b) => b.score - a.score);
        const topK = scoredDocs.slice(0, parseInt(k)).map(d => d.text);

        res.json({ results: topK });

    } catch (error) {
        console.error("RAG Search Error", error);
        res.status(500).json({ error: "Failed to search similar texts" });
    }
}
