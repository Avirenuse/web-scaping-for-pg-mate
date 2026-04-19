import mongoose from 'mongoose';

const documentSchema = new mongoose.Schema({
  text: { type: String, required: true },
  embedding: { type: [Number], required: true }, // Array of floats for vector search
  createdAt: { type: Date, default: Date.now }
});

export default mongoose.model('Document', documentSchema);
