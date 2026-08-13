import { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import api from '../api/client';
import ChatMessage from '../components/Chat/ChatMessage';
import AgentProgress from '../components/Chat/AgentProgress';
import LoadingSpinner from '../components/common/LoadingSpinner';
import './Chat.css';

export default function Chat() {
  const location = useLocation();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [agents, setAgents] = useState([]);
  const [threadId, setThreadId] = useState(null);
  const [error, setError] = useState('');
  const chatEndRef = useRef(null);
  const inputRef = useRef(null);

  // Handle query passed from dashboard
  useEffect(() => {
    if (location.state?.query) {
      setInput(location.state.query);
      // Clear the state so it doesn't re-trigger
      window.history.replaceState({}, document.title);
    }
  }, [location.state]);

  // Auto-scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSend = async () => {
    const query = input.trim();
    if (!query || loading) return;

    setError('');
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: query }]);
    setLoading(true);

    // Initial real agent pipeline state
    setAgents([
      { agent: 'player_agent', status: 'pending' },
      { agent: 'research_agent', status: 'pending' },
      { agent: 'analysis_agent', status: 'pending' },
      { agent: 'final_agent', status: 'pending' },
    ]);

    await api.streamChat(
      query,
      threadId,
      // Real-time backend event callback
      (evt) => {
        if (evt.thread_id) setThreadId(evt.thread_id);
        if (evt.event === 'start' && evt.agents) {
          setAgents(evt.agents);
        } else if (evt.event === 'agent_start') {
          setAgents((prev) =>
            prev.map((ag) => (ag.agent === evt.agent ? { ...ag, status: 'running' } : ag))
          );
        } else if (evt.event === 'agent_completed') {
          setAgents((prev) =>
            prev.map((ag) => (ag.agent === evt.agent ? { ...ag, status: 'completed' } : ag))
          );
        }
      },
      // Completion callback
      (finishData) => {
        if (finishData.thread_id) setThreadId(finishData.thread_id);
        setAgents((prev) => prev.map((ag) => ({ ...ag, status: 'completed' })));
        setMessages((prev) => [
          ...prev,
          {
            role: 'ai',
            content: finishData.final_response || 'No response generated.',
            sources: finishData.sources || [],
          },
        ]);

        const recent = JSON.parse(localStorage.getItem('recentSearches') || '[]');
        recent.unshift({ query, time: new Date().toLocaleString() });
        localStorage.setItem('recentSearches', JSON.stringify(recent.slice(0, 20)));
        setLoading(false);
      },
      // Error callback
      (err) => {
        setError(err.message || 'Stream processing failed');
        setAgents((prev) =>
          prev.map((ag) =>
            ag.status === 'running' || ag.status === 'pending' ? { ...ag, status: 'failed' } : ag
          )
        );
        setLoading(false);
      }
    );
  };


  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setThreadId(null);
    setAgents([]);
    setError('');
    inputRef.current?.focus();
  };

  return (
    <div className="chat-page animate-fade-in">
      {/* Header */}
      <div className="chat-header">
        <div>
          <h1 className="chat-title">
            <span className="gradient-text">AI Football Chat</span>
          </h1>
          <p className="chat-subtitle">
            Ask anything about football players, tactics, and transfers
          </p>
        </div>
        <div className="chat-header-actions">
          {threadId && (
            <span className="badge badge-blue">Thread: {threadId.slice(0, 16)}...</span>
          )}
          <button className="btn btn-secondary btn-sm" onClick={handleNewChat}>
            + New Chat
          </button>
        </div>
      </div>

      {/* Agent progress */}
      {(loading || agents.length > 0) && (
        <AgentProgress agents={agents} isLoading={loading} />
      )}

      {/* Messages */}
      <div className="chat-messages">
        {messages.length === 0 && !loading && (
          <div className="chat-welcome">
            <div className="chat-welcome-icon">💬</div>
            <h2>Welcome to Football AI Chat</h2>
            <p>Ask me anything about football. Try:</p>
            <div className="chat-suggestions">
              {[
                'Analyze Erling Haaland',
                'Compare Messi and Ronaldo',
                'Find a young striker under 23',
                'Best midfielders in Premier League',
              ].map((q) => (
                <button
                  key={q}
                  className="chat-suggestion-chip"
                  onClick={() => { setInput(q); inputRef.current?.focus(); }}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <ChatMessage key={i} role={msg.role} content={msg.content} />
        ))}

        {loading && (
          <div className="chat-loading">
            <LoadingSpinner text="Agents are working..." size="sm" />
          </div>
        )}

        {error && (
          <div className="chat-error">
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Input */}
      <div className="chat-input-container">
        <div className="chat-input-wrapper">
          <input
            ref={inputRef}
            type="text"
            className="chat-input input"
            placeholder="Ask about any football player, team, or comparison..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
            maxLength={2000}
          />
          <button
            className="btn btn-primary chat-send-btn"
            onClick={handleSend}
            disabled={!input.trim() || loading}
          >
            {loading ? '⏳' : '→'}
          </button>
        </div>
        <p className="chat-input-hint">
          Press Enter to send • Powered by Groq + LangGraph Multi-Agent System
        </p>
      </div>
    </div>
  );
}
