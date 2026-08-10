import { useState, useRef, useEffect } from 'react';
import './Chat.css';
import api from '../api/api';

interface Message {
  role: 'user' | 'assistant';
  text: string;
}

const generateSessionId = () => 'session_' + Math.random().toString(36).substring(2, 10);

const Chat = () => {
  const [sessionId, setSessionId] = useState<string>(generateSessionId);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = 'auto';
      el.style.height = `${el.scrollHeight}px`;
    }
  }, [input]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleNewChat = () => {
    setSessionId(generateSessionId());
    setMessages([]);
    setInput('');
  };

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage = input.trim();
    setMessages((prev) => [...prev, { role: 'user', text: userMessage }]);
    setInput('');
    setLoading(true);

    api.post('/chat', { prompt: userMessage, session_id: sessionId })
      .then((response) => {
        console.log("setResponse", response.data);
        const answer = response.data?.answer || 'Received an empty response. Please try again.';
        setMessages((prev) => [...prev, { role: 'assistant', text: answer }]);
      })
      .catch((error) => {
        console.error(error);
        const errorMsg = error.response?.data?.detail || 'Something went wrong. Please try again.';
        setMessages((prev) => [...prev, { role: 'assistant', text: errorMsg }]);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="chat-header-title">
          <span className="chat-header-badge">RAG Assistant</span>
        </div>
        <button 
          className="chat-new-btn" 
          onClick={handleNewChat} 
          title="Start a new conversation"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 5v14M5 12h14"/>
          </svg>
          New Chat
        </button>
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-empty-state">
            <div className="chat-empty-icon">✦</div>
            <h2>How can I help you today?</h2>
            <p>Ask questions based on the uploaded document.</p>
          </div>
        ) : (
          messages.map((msg, i) => (
            <div key={i} className={`chat-message ${msg.role}`}>
              {msg.text}
            </div>
          ))
        )}

        {loading && (
          <div className="chat-message assistant">
            <div className="typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <div className="chat-input-bar">
          <textarea
            ref={textareaRef}
            className="chat-input"
            rows={1}
            placeholder="Message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button
            className={`chat-send-btn ${input.trim() ? 'active' : ''}`}
            onClick={handleSend}
            disabled={!input.trim() || loading}
            aria-label="Send message"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chat;
