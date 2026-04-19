import mongoose from 'mongoose';

const flashcardSchema = new mongoose.Schema({
  question: { type: String, required: true },
  answer: { type: String, required: true },
  sourceTextSnippet: { type: String, default: "" },
  createdAt: { type: Date, default: Date.now }
});

export default mongoose.model('Flashcard', flashcardSchema);
