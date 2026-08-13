import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import './Dashboard.css';

const quickActions = [
  { label: 'Analyze a Player', icon: '⚽', path: '/chat', query: 'Analyze ' },
  { label: 'Compare Players', icon: '⚔️', path: '/compare' },
  { label: 'AI Scout', icon: '🎯', path: '/scout' },
  { label: 'Search Players', icon: '🔍', path: '/players' },
];

const exampleQueries = [
  'Analyze Erling Haaland',
  'Compare Haaland and Mbappe',
  'Find a midfielder similar to Bruno Fernandes',
  'Recommend a striker for Arsenal',
  'Who is leading the Premier League standings?',
  'Scouting report for Jude Bellingham',
];

export default function Dashboard() {
  const navigate = useNavigate();
  const [health, setHealth] = useState(null);
  const [recentSearches, setRecentSearches] = useState([]);

  useEffect(() => {
    api.healthCheck()
      .then(setHealth)
      .catch(() => setHealth({ status: 'error' }));

    const saved = localStorage.getItem('recentSearches');
    if (saved) {
      try { setRecentSearches(JSON.parse(saved)); } catch {}
    }
  }, []);

  return (
    <div className="dashboard animate-fade-in">
      {/* Hero section */}
      <div className="dashboard-hero">
        <div className="dashboard-hero-content">
          <h1 className="dashboard-title">
            <span className="gradient-text">Football Intelligence</span>
            <br />& Scouting Platform
          </h1>
          <p className="dashboard-subtitle">
            Multi-Agent AI • 5 Football APIs • API-Football • Sportmonks • TheSportsDB • Football-Data • Tavily
          </p>
          <div className="dashboard-hero-actions">
            <button className="btn btn-primary btn-lg" onClick={() => navigate('/chat')}>
              💬 Start AI Chat
            </button>
            <button className="btn btn-secondary btn-lg" onClick={() => navigate('/scout')}>
              🎯 AI Scout
            </button>
          </div>
        </div>
        <div className="dashboard-hero-visual">
          <div className="hero-orb hero-orb-1" />
          <div className="hero-orb hero-orb-2" />
          <div className="hero-orb hero-orb-3" />
          <div className="hero-football">⚽</div>
        </div>
      </div>

      {/* Status cards for all integrations */}
      <h2 className="section-title">Data Sources & System Health</h2>
      <div className="dashboard-status-grid stagger-children" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))' }}>
        <div className="status-card glass-card">
          <div className="status-card-icon">🗄️</div>
          <div className="status-card-info">
            <span className="status-card-label">Database</span>
            <span className={`status-card-value ${health?.database === 'connected' ? 'text-green' : 'text-red'}`}>
              {health?.database || 'Checking...'}
            </span>
          </div>
        </div>
        <div className="status-card glass-card">
          <div className="status-card-icon">🧠</div>
          <div className="status-card-info">
            <span className="status-card-label">Groq LLM</span>
            <span className={`status-card-value ${health?.groq_configured ? 'text-green' : 'text-red'}`}>
              {health?.groq_configured ? 'Connected' : 'Not configured'}
            </span>
          </div>
        </div>
        <div className="status-card glass-card">
          <div className="status-card-icon">⚽</div>
          <div className="status-card-info">
            <span className="status-card-label">API-Football</span>
            <span className={`status-card-value ${health?.football_api_configured ? 'text-green' : 'text-red'}`}>
              {health ? (health.football_api_configured ? `Season ${health.football_season}` : 'Not configured') : 'Checking...'}
            </span>
          </div>
        </div>
        <div className="status-card glass-card">
          <div className="status-card-icon">👑</div>
          <div className="status-card-info">
            <span className="status-card-label">Sportmonks</span>
            <span className={`status-card-value ${health?.sportmonks_configured ? 'text-green' : 'text-red'}`}>
              {health?.sportmonks_configured ? 'Connected' : 'Not configured'}
            </span>
          </div>
        </div>
        <div className="status-card glass-card">
          <div className="status-card-icon">🖼️</div>
          <div className="status-card-info">
            <span className="status-card-label">TheSportsDB</span>
            <span className={`status-card-value ${health?.thesportsdb_configured ? 'text-green' : 'text-red'}`}>
              {health?.thesportsdb_configured ? 'Connected' : 'Not configured'}
            </span>
          </div>
        </div>
        <div className="status-card glass-card">
          <div className="status-card-icon">📊</div>
          <div className="status-card-info">
            <span className="status-card-label">Football-Data</span>
            <span className={`status-card-value ${health?.football_data_configured ? 'text-green' : 'text-red'}`}>
              {health?.football_data_configured ? 'Connected' : 'Not configured'}
            </span>
          </div>
        </div>
        <div className="status-card glass-card">
          <div className="status-card-icon">🔎</div>
          <div className="status-card-info">
            <span className="status-card-label">Tavily Search</span>
            <span className={`status-card-value ${health?.tavily_configured ? 'text-green' : 'text-red'}`}>
              {health?.tavily_configured ? 'Connected' : 'Not configured'}
            </span>
          </div>
        </div>
      </div>

      {/* Quick actions */}
      <section className="dashboard-section">
        <h2 className="section-title">Quick Actions</h2>
        <div className="quick-actions-grid stagger-children">
          {quickActions.map((action) => (
            <button
              key={action.label}
              className="quick-action-card glass-card"
              onClick={() => navigate(action.path)}
            >
              <span className="quick-action-icon">{action.icon}</span>
              <span className="quick-action-label">{action.label}</span>
            </button>
          ))}
        </div>
      </section>

      {/* Example queries */}
      <section className="dashboard-section">
        <h2 className="section-title">Try These Queries</h2>
        <div className="example-queries stagger-children">
          {exampleQueries.map((q) => (
            <button
              key={q}
              className="example-query-chip"
              onClick={() => navigate('/chat', { state: { query: q } })}
            >
              {q}
            </button>
          ))}
        </div>
      </section>

      {/* Recent searches */}
      {recentSearches.length > 0 && (
        <section className="dashboard-section">
          <h2 className="section-title">Recent Searches</h2>
          <div className="recent-list stagger-children">
            {recentSearches.slice(0, 5).map((search, i) => (
              <div key={i} className="recent-item glass-card" onClick={() => navigate('/chat', { state: { query: search.query } })}>
                <span className="recent-icon">💬</span>
                <div className="recent-info">
                  <span className="recent-query">{search.query}</span>
                  <span className="recent-time">{search.time}</span>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Pipeline info */}
      <section className="dashboard-section">
        <h2 className="section-title">Multi-Source Agent Pipeline</h2>
        <div className="pipeline-visual">
          {['Player Agent', 'Research Agent', 'Analysis Agent', 'Final Agent'].map((agent, i) => (
            <div key={agent} className="pipeline-node-wrapper">
              <div className="pipeline-node glass-card">
                <span className="pipeline-node-icon">{['⚽', '🔎', '📊', '✨'][i]}</span>
                <span className="pipeline-node-label">{agent}</span>
                <span className="pipeline-node-desc">
                  {['API-Football, Sportmonks, TheSportsDB', 'Football-Data.org & Tavily Web Search', 'LLM Analysis', 'Source Attribution Response'][i]}
                </span>
              </div>
              {i < 3 && <span className="pipeline-arrow">→</span>}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
