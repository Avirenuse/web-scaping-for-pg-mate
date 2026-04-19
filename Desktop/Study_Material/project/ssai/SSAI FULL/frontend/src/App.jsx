import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import { BrainCircuit, Image as ImageIcon, BookOpen, Search, ArrowRight, Clock, Play, Square, CheckCircle, XCircle } from 'lucide-react';

const API_BASE = 'http://localhost:5000/api';

const QUOTES = [
  "Success is the sum of small efforts, repeated day in and day out.",
  "The secret to getting ahead is getting started.",
  "It always seems impossible until it's done.",
  "Don't watch the clock; do what it does. Keep going.",
  "The beautiful thing about learning is that no one can take it away from you."
];

function PomodoroTimer() {
  const [timeLeft, setTimeLeft] = useState(25 * 60);
  const [isActive, setIsActive] = useState(false);

  useEffect(() => {
    let interval = null;
    if (isActive && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((time) => time - 1);
      }, 1000);
    } else if (timeLeft === 0) {
      setIsActive(false);
    }
    return () => clearInterval(interval);
  }, [isActive, timeLeft]);

  const toggleTimer = () => setIsActive(!isActive);
  const resetTimer = () => { setIsActive(false); setTimeLeft(25 * 60); };

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="glass-panel perspective-panel timer-widget" style={{ textAlign: 'center', padding: '1.5rem', marginBottom: '2rem' }}>
      <h3 style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', color: 'var(--accent-secondary)' }}>
        <Clock size={20} /> Focus Timer
      </h3>
      <div className="timer-display" style={{ fontSize: '3.5rem', fontWeight: 'bold', margin: '1rem 0', textShadow: '0 0 20px rgba(135,100,250,0.5)', fontFamily: 'monospace' }}>
        {formatTime(timeLeft)}
      </div>
      <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem' }}>
        <button className="btn btn-primary" onClick={toggleTimer} style={{ padding: '0.6rem 1.2rem', fontSize: '0.9rem' }}>
          {isActive ? <Square size={16} /> : <Play size={16} />} 
          {isActive ? 'Pause' : 'Start'}
        </button>
        <button className="btn btn-secondary" onClick={resetTimer} style={{ padding: '0.6rem 1.2rem', fontSize: '0.9rem' }}>
          Reset
        </button>
      </div>
    </div>
  );
}

function Home({ 
  text, setText, 
  handleImageUpload, 
  handleGenerateFlashcards, 
  handleRAGSearch, 
  ragResults, 
  loading 
}) {
  const [numCards, setNumCards] = useState(5);
  const [quote] = useState(QUOTES[Math.floor(Math.random() * QUOTES.length)]);

  return (
    <div className="grid">
      <header style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
        <h1 className="title-gradient interactive-element" style={{ fontSize: '3rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1rem' }}>
          <BrainCircuit size={48} color="var(--accent-primary)" />
          Study Buddy
        </h1>
        <p className="subtitle" style={{ fontStyle: 'italic', marginTop: '0.5rem', fontSize: '1.1rem' }}>
          "{quote}"
        </p>
      </header>

      <div className="grid grid-cols-2" style={{ gap: '2rem' }}>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <div className="glass-panel perspective-panel" style={{ flexGrow: 1 }}>
            <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
              <ImageIcon /> Document Upload (PDF/Image)
            </h2>
            <input 
              type="file" 
              accept="image/*,application/pdf" 
              onChange={handleImageUpload} 
              disabled={loading}
              style={{ marginBottom: '1rem' }}
            />
            {loading && <p style={{ color: 'var(--accent-primary)' }}>Loading processing...</p>}
            
            <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', marginTop: '2rem' }}>
              <BookOpen /> Document Text
            </h2>
            <textarea 
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste text here or upload a document to instantly extract text..."
            />
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <PomodoroTimer />

          <div className="glass-panel perspective-panel" style={{ flexGrow: 1 }}>
            <h2>Study Toolkit</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem', marginTop: '1.5rem' }}>
              <div>
                <label>Number of Flashcards to Create</label>
                <input 
                  type="number" 
                  min="1" max="50" 
                  value={numCards} 
                  onChange={(e) => setNumCards(e.target.value)} 
                />
              </div>
              
              <button className="btn btn-primary" onClick={() => handleGenerateFlashcards(numCards)} disabled={!text || loading}>
                Generate AI Flashcards
              </button>
              <Link to="/flashcards" className="btn btn-secondary" style={{ textAlign: 'center' }}>
                View Saved Flashcards
              </Link>

              <hr style={{ borderColor: 'var(--glass-border)', margin: '1rem 0' }} />

              <button className="btn btn-secondary" onClick={handleRAGSearch} disabled={!text || loading} style={{ display: 'flex', justifyContent: 'center' }}>
                <Search size={18}/> 🧠 Smart Deep Dive (Find Context)
              </button>
            </div>
          </div>
        </div>
      </div>

      {ragResults.length > 0 && (
        <div className="glass-panel perspective-panel" style={{ marginTop: '2rem' }}>
          <h2>🧠 AI Document Insights</h2>
          <div className="grid" style={{ marginTop: '1rem' }}>
            {ragResults.map((result, idx) => (
              <div key={idx} style={{ padding: '1rem', background: 'rgba(0,0,0,0.3)', borderRadius: '8px', borderLeft: '4px solid var(--accent-primary)' }}>
                {result}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function FlashcardsView({ flashcards }) {
  const [mastered, setMastered] = useState(new Set());

  if (!flashcards || flashcards.length === 0) {
    return (
      <div className="glass-panel" style={{ textAlign: 'center', marginTop: '3rem' }}>
        <h2>No Flashcards Available</h2>
        <p className="subtitle" style={{ margin: '1rem 0' }}>It looks empty here. Go back and generate some from your text!</p>
        <Link to="/" className="btn btn-primary">Go Back</Link>
      </div>
    );
  }

  const handleMastery = (idx, isMastered) => {
    setMastered(prev => {
      const newSet = new Set(prev);
      if (isMastered) newSet.add(idx);
      else newSet.delete(idx);
      return newSet;
    });
  };

  const progress = Math.round((mastered.size / flashcards.length) * 100);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h1 className="title-gradient">Mastery Session</h1>
        <Link to="/" className="btn btn-secondary">← Back to Overview</Link>
      </div>

      <div className="glass-panel perspective-panel" style={{ padding: '1.5rem', marginBottom: '3rem', position: 'relative', zIndex: 10 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.8rem' }}>
          <span style={{ fontWeight: 'bold', fontSize: '1.2rem' }}>Overall Mastery</span>
          <span style={{ color: 'var(--accent-primary)', fontWeight: 'bold', fontSize: '1.2rem' }}>{progress}%</span>
        </div>
        <div className="progress-bar-bg" style={{ width: '100%', height: '12px', background: 'rgba(0,0,0,0.3)', borderRadius: '10px', overflow: 'hidden' }}>
          <div className="progress-bar-fill" style={{ 
            width: `${progress}%`, 
            height: '100%', 
            background: 'linear-gradient(90deg, var(--accent-primary), var(--accent-secondary))',
            transition: 'width 0.5s cubic-bezier(0.22, 1, 0.36, 1)'
          }}></div>
        </div>
      </div>
      
      <div className="grid grid-cols-3">
        {flashcards.map((card, idx) => {
          const [flipped, setFlipped] = React.useState(false);
          const isCardMastered = mastered.has(idx);

          return (
            <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', transition: 'all 0.3s', opacity: isCardMastered ? 0.7 : 1 }}>
              <div 
                className={`flashcard-wrapper ${flipped ? 'flipped' : ''}`}
                onClick={() => setFlipped(!flipped)}
                style={{ marginBottom: '0.5rem' }}
              >
                <div className="flashcard-inner" style={{ border: isCardMastered ? '2px solid lightgreen' : '' }}>
                  <div className="flashcard-front">
                    <h3 style={{ marginBottom: '1rem', color: 'var(--accent-secondary)' }}>Question {idx + 1}</h3>
                    <p>{card.question}</p>
                  </div>
                  <div className="flashcard-back">
                    <h3 style={{ marginBottom: '1rem' }}>Answer</h3>
                    <p>{card.answer}</p>
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem' }} className="mastery-buttons">
                <button 
                  className="btn btn-secondary" 
                  onClick={(e) => { e.stopPropagation(); handleMastery(idx, false); }}
                  style={{ padding: '0.6rem', fontSize: '0.9rem', flex: 1, borderColor: !isCardMastered ? 'tomato' : '' }}
                >
                  <XCircle size={16} style={{ color: 'tomato' }} /> Study
                </button>
                <button 
                  className="btn btn-secondary" 
                  onClick={(e) => { e.stopPropagation(); handleMastery(idx, true); }}
                  style={{ padding: '0.6rem', fontSize: '0.9rem', flex: 1, borderColor: isCardMastered ? 'lightgreen' : '' }}
                >
                  <CheckCircle size={16} style={{ color: 'lightgreen' }} /> Mastered
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function App() {
  const [text, setText] = useState('');
  const [flashcards, setFlashcards] = useState([]);
  const [ragResults, setRagResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleImageUpload = async (e) => {
    if (!e.target.files[0]) return;
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('image', e.target.files[0]); // Handles both PDF and Image gracefully on backend
      
      const res = await fetch(`${API_BASE}/extract-text`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (data.text) {
        setText(data.text);
        
        await fetch(`${API_BASE}/rag/add`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: data.text })
        });
      }
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const handleGenerateFlashcards = async (numCards) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/flashcards`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, numCards })
      });
      const data = await res.json();
      if (data.flashcards) {
        setFlashcards(data.flashcards);
        navigate('/flashcards');
      }
    } catch(err) {
      console.error(err);
    }
    setLoading(false);
  };

  const handleRAGSearch = async () => {
    setLoading(true);
    try {
        const res = await fetch(`${API_BASE}/rag/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: text, k: 3 })
        });
        const data = await res.json();
        if (data.results) {
            setRagResults(data.results);
        }
    } catch(err) {
        console.error(err);
    }
    setLoading(false);
  }

  return (
    <Routes>
      <Route path="/" element={
        <Home 
          text={text} 
          setText={setText}
          handleImageUpload={handleImageUpload}
          handleGenerateFlashcards={handleGenerateFlashcards}
          handleRAGSearch={handleRAGSearch}
          ragResults={ragResults}
          loading={loading}
        />
      } />
      <Route path="/flashcards" element={<FlashcardsView flashcards={flashcards} />} />
    </Routes>
  );
}

export default App;
