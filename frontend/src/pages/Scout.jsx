import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import api from '../api/client';
import LoadingSpinner from '../components/common/LoadingSpinner';
import AgentProgress from '../components/Chat/AgentProgress';
import PlayerCard from '../components/Player/PlayerCard';
import './Scout.css';

const scoutExamples = [
  'Young right winger under 23 with pace and dribbling',
  'Fast striker with strong finishing under 25',
  'Find a midfielder similar to Bruno Fernandes',
  'Left-back with good crossing ability',
  'Young centre-back with leadership qualities',
  'Creative playmaker for a mid-table Premier League team',
];

export default function Scout() {
  const [requirements, setRequirements] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleScout = async () => {
    const req = requirements.trim();
    if (!req) return;

    setError('');
    setLoading(true);
    setResult(null);

    try {
      const data = await api.runScout(req);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="scout-page animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">
          <span className="gradient-text">AI Scout</span>
        </h1>
        <p className="page-subtitle">
          Describe your ideal player and let AI find real candidate matches from live football APIs
        </p>
      </div>

      {/* Input */}
      <div className="scout-input-section glass-card">
        <label className="scout-label">Scouting Requirements</label>
        <textarea
          className="input textarea scout-textarea"
          placeholder="Describe the type of player you're looking for..."
          value={requirements}
          onChange={(e) => setRequirements(e.target.value)}
          maxLength={2000}
          rows={4}
        />
        <div className="scout-input-footer">
          <span className="scout-char-count">{requirements.length}/2000</span>
          <button
            className="btn btn-primary btn-lg"
            onClick={handleScout}
            disabled={!requirements.trim() || loading}
          >
            🎯 Run AI Scout
          </button>
        </div>
      </div>

      {/* Examples */}
      <div className="scout-examples">
        <span className="scout-examples-label">Try:</span>
        {scoutExamples.map((ex) => (
          <button
            key={ex}
            className="example-query-chip"
            onClick={() => setRequirements(ex)}
          >
            {ex}
          </button>
        ))}
      </div>

      {error && <div className="search-error">⚠️ {error}</div>}

      {loading && (
        <>
          <AgentProgress agents={[]} isLoading={true} />
          <LoadingSpinner text="Multi-agent scouting engine is retrieving and comparing candidate statistics..." />
        </>
      )}

      {/* Report */}
      {result && !loading && (
        <div className="scout-report animate-fade-in">
          <div className="scout-report-header glass-card">
            <div>
              <h2 className="scout-report-title">Scouting Report</h2>
              <p className="scout-report-req">
                <strong>Requirements:</strong> {result.requirements}
              </p>
              {result.sources && result.sources.length > 0 && (
                <div style={{ display: 'flex', gap: '6px', marginTop: '8px', flexWrap: 'wrap' }}>
                  <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Data Sources:</span>
                  {result.sources.map((s, i) => (
                    <span key={i} className="badge badge-blue">{s}</span>
                  ))}
                </div>
              )}
            </div>
            <span className="source-tag source-tag-ai">AI Multi-Agent Report</span>
          </div>

          {/* Real Candidate Player Cards */}
          {result.candidates && result.candidates.length > 0 && (
            <div className="scout-candidates-section" style={{ marginTop: '24px' }}>
              <h3 style={{ fontSize: '1.25rem', marginBottom: '12px' }}>Real Candidate Players Evaluated</h3>
              <div className="players-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '16px' }}>
                {result.candidates.map((player, idx) => (
                  <PlayerCard key={idx} player={player} />
                ))}
              </div>
            </div>
          )}

          <div className="scout-report-body glass-card" style={{ marginTop: '24px' }}>
            <ReactMarkdown>{result.report}</ReactMarkdown>
          </div>

          {result.player_data && (
            <details className="scout-raw-data glass-card">
              <summary className="scout-raw-summary">
                <span className="source-tag source-tag-api">Retrieved Player Data</span>
                View raw player data passed to agents
              </summary>
              <pre className="scout-raw-content">{result.player_data}</pre>
            </details>
          )}

          {result.web_research && (
            <details className="scout-raw-data glass-card">
              <summary className="scout-raw-summary">
                <span className="source-tag source-tag-web">Web Research</span>
                View web research data
              </summary>
              <pre className="scout-raw-content">{result.web_research}</pre>
            </details>
          )}
        </div>
      )}
    </div>
  );
}
