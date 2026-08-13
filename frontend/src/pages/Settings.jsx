import { useState, useEffect } from 'react';
import api from '../api/client';
import './Settings.css';

export default function Settings() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [recentSearches, setRecentSearches] = useState([]);

  useEffect(() => {
    setLoading(true);
    api.healthCheck()
      .then((data) => {
        setHealth(data);
        setError(null);
      })
      .catch((err) => {
        setHealth(null);
        setError(err.message || 'Unable to connect to backend server');
      })
      .finally(() => setLoading(false));

    const saved = localStorage.getItem('recentSearches');
    if (saved) {
      try { setRecentSearches(JSON.parse(saved)); } catch {}
    }
  }, []);

  const clearHistory = () => {
    localStorage.removeItem('recentSearches');
    setRecentSearches([]);
  };

  return (
    <div className="settings-page animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">
          <span className="gradient-text">Settings & About</span>
        </h1>
      </div>

      {/* System status */}
      <section className="settings-section glass-card">
        <h2 className="settings-section-title">System Status</h2>
        <div style={{ marginBottom: '12px', fontSize: '0.85rem', color: '#94a3b8' }}>
          Backend Target: <code>{api.getBaseUrl()}</code>
        </div>
        {error && (
          <div className="search-error" style={{ marginBottom: '16px' }}>
            ⚠️ Backend Connection Error: {error}
          </div>
        )}
        <div className="settings-status-grid">
          <div className="settings-status-row">
            <span className="settings-status-label">Overall Status</span>
            <span className={`badge ${loading ? '' : (health?.status === 'healthy' ? 'badge-green' : 'badge-red')}`}>
              {loading ? 'Checking...' : (health?.status || 'Disconnected')}
            </span>
          </div>
          <div className="settings-status-row">
            <span className="settings-status-label">PostgreSQL Database</span>
            <span className={`badge ${loading ? '' : (health?.database === 'connected' ? 'badge-green' : 'badge-red')}`}>
              {loading ? 'Checking...' : (health?.database || 'Disconnected')}
            </span>
          </div>
          <div className="settings-status-row">
            <span className="settings-status-label">Groq LLM (Llama 3.3 70B)</span>
            <span className={`badge ${loading ? '' : (health?.groq_configured ? 'badge-green' : 'badge-red')}`}>
              {loading ? 'Checking...' : (health?.groq_configured ? 'Configured' : 'Not configured')}
            </span>
          </div>
          <div className="settings-status-row">
            <span className="settings-status-label">API-Football</span>
            <span className={`badge ${loading ? '' : (health?.football_api_configured ? 'badge-green' : 'badge-red')}`}>
              {loading ? 'Checking...' : (health?.football_api_configured ? `Season ${health.football_season}` : 'Not configured')}
            </span>
          </div>
          <div className="settings-status-row">
            <span className="settings-status-label">Tavily Web Search</span>
            <span className={`badge ${loading ? '' : (health?.tavily_configured ? 'badge-green' : 'badge-red')}`}>
              {loading ? 'Checking...' : (health?.tavily_configured ? 'Configured' : 'Not configured')}
            </span>
          </div>
        </div>
      </section>


      {/* Chat history */}
      <section className="settings-section glass-card">
        <div className="settings-section-header">
          <h2 className="settings-section-title">Chat History</h2>
          {recentSearches.length > 0 && (
            <button className="btn btn-secondary btn-sm" onClick={clearHistory}>
              Clear History
            </button>
          )}
        </div>
        {recentSearches.length > 0 ? (
          <div className="settings-history-list">
            {recentSearches.map((item, i) => (
              <div key={i} className="settings-history-item">
                <span className="settings-history-query">{item.query}</span>
                <span className="settings-history-time">{item.time}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="settings-empty">No recent searches.</p>
        )}
      </section>

      {/* About */}
      <section className="settings-section glass-card">
        <h2 className="settings-section-title">About This Project</h2>
        <div className="about-content">
          <p>
            <strong>AI Football Intelligence & Player Recommendation System</strong> is a
            full-stack application combining multi-agent AI architecture with real football data.
          </p>

          <h3>Technology Stack</h3>
          <div className="tech-grid">
            {[
              { name: 'LangGraph', desc: 'Multi-agent orchestration' },
              { name: 'Groq + Llama 3.3 70B', desc: 'Large Language Model' },
              { name: 'API-Football', desc: 'Structured player data' },
              { name: 'Tavily', desc: 'Real-time web research' },
              { name: 'PostgreSQL', desc: 'Conversation memory' },
              { name: 'FastAPI', desc: 'Backend API server' },
              { name: 'React + Vite', desc: 'Frontend framework' },
              { name: 'Chart.js', desc: 'Data visualization' },
            ].map((tech) => (
              <div key={tech.name} className="tech-item">
                <span className="tech-name">{tech.name}</span>
                <span className="tech-desc">{tech.desc}</span>
              </div>
            ))}
          </div>

          <h3>Multi-Agent Pipeline</h3>
          <p>
            Each query passes through 4 specialized agents:
          </p>
          <ol>
            <li><strong>Player Agent</strong> — Retrieves structured data from API-Football</li>
            <li><strong>Research Agent</strong> — Searches the web via Tavily for recent information</li>
            <li><strong>Analysis Agent</strong> — Analyzes all data with LLM-powered intelligence</li>
            <li><strong>Final Agent</strong> — Generates a comprehensive, formatted response</li>
          </ol>
        </div>
      </section>
    </div>
  );
}
