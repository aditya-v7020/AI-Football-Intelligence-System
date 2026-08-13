import { useState } from 'react';
import { Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';
import ReactMarkdown from 'react-markdown';
import api from '../api/client';
import LoadingSpinner from '../components/common/LoadingSpinner';
import AgentProgress from '../components/Chat/AgentProgress';
import './PlayerComparison.css';

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

export default function PlayerComparison() {
  const [player1, setPlayer1] = useState('');
  const [player2, setPlayer2] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleCompare = async () => {
    const p1 = player1.trim();
    const p2 = player2.trim();
    if (!p1 || !p2) return;

    if (p1.toLowerCase() === p2.toLowerCase()) {
      setError('Please enter two different players.');
      return;
    }

    setError('');
    setLoading(true);
    setResult(null);

    try {
      const data = await api.comparePlayers(p1, p2);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Build radar chart data from the first matched player of each set
  const getRadarData = () => {
    if (!result) return null;

    const p1 = result.player1_data?.[0];
    const p2 = result.player2_data?.[0];

    if (!p1 && !p2) return null;

    return {
      labels: ['Goals', 'Assists', 'Appearances', 'Shots on Target', 'Dribbles', 'Tackles'],
      datasets: [
        {
          label: p1?.name || player1,
          data: [
            p1?.goals || 0,
            p1?.assists || 0,
            Math.min(p1?.appearances || 0, 40),
            p1?.shots_on_target || 0,
            p1?.dribbles_success || 0,
            p1?.tackles_total || 0,
          ],
          backgroundColor: 'rgba(0, 230, 118, 0.15)',
          borderColor: 'rgba(0, 230, 118, 0.8)',
          borderWidth: 2,
          pointBackgroundColor: '#00e676',
        },
        {
          label: p2?.name || player2,
          data: [
            p2?.goals || 0,
            p2?.assists || 0,
            Math.min(p2?.appearances || 0, 40),
            p2?.shots_on_target || 0,
            p2?.dribbles_success || 0,
            p2?.tackles_total || 0,
          ],
          backgroundColor: 'rgba(66, 165, 245, 0.15)',
          borderColor: 'rgba(66, 165, 245, 0.8)',
          borderWidth: 2,
          pointBackgroundColor: '#42a5f5',
        },
      ],
    };
  };

  const radarOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
        labels: { color: '#94a3b8', font: { family: 'Inter' } },
      },
    },
    scales: {
      r: {
        grid: { color: 'rgba(148, 163, 184, 0.1)' },
        angleLines: { color: 'rgba(148, 163, 184, 0.1)' },
        ticks: { color: '#64748b', backdropColor: 'transparent' },
        pointLabels: { color: '#94a3b8', font: { family: 'Inter', size: 11 } },
      },
    },
  };

  const renderPlayerColumn = (data, label) => {
    const player = data?.[0];
    if (!player) {
      return (
        <div className="compare-column">
          <h3 className="compare-col-title">{label}</h3>
          <p className="compare-no-data">No data found</p>
        </div>
      );
    }

    return (
      <div className="compare-column">
        <div className="compare-player-header">
          {player.photo && <img src={player.photo} alt={player.name} className="compare-photo" />}
          <h3 className="compare-player-name">{player.name}</h3>
          <span className="badge badge-green">{player.position}</span>
        </div>
        <div className="compare-details">
          {[
            { label: 'Team', value: player.team },
            { label: 'League', value: player.league },
            { label: 'Age', value: player.age },
            { label: 'Nationality', value: player.nationality },
            { label: 'Goals', value: player.goals },
            { label: 'Assists', value: player.assists },
            { label: 'Appearances', value: player.appearances },
            { label: 'Minutes', value: player.minutes },
            { label: 'Rating', value: player.rating || '—' },
            { label: 'Yellow Cards', value: player.yellow_cards },
            { label: 'Red Cards', value: player.red_cards },
          ].map((item) => (
            <div key={item.label} className="compare-detail-row">
              <span className="compare-detail-label">{item.label}</span>
              <span className="compare-detail-value">{item.value ?? '—'}</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const radarData = getRadarData();

  return (
    <div className="comparison-page animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">
          <span className="gradient-text">Player Comparison</span>
        </h1>
        <p className="page-subtitle">
          Compare two players side-by-side with stats, charts, and AI analysis
        </p>
      </div>

      {/* Input */}
      <div className="compare-inputs glass-card">
        <div className="compare-input-group">
          <label className="compare-label">Player 1</label>
          <input
            type="text"
            className="input"
            placeholder="e.g. Haaland"
            value={player1}
            onChange={(e) => setPlayer1(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleCompare()}
            maxLength={200}
          />
        </div>
        <div className="compare-vs">VS</div>
        <div className="compare-input-group">
          <label className="compare-label">Player 2</label>
          <input
            type="text"
            className="input"
            placeholder="e.g. Mbappe"
            value={player2}
            onChange={(e) => setPlayer2(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleCompare()}
            maxLength={200}
          />
        </div>
        <button
          className="btn btn-primary btn-lg compare-btn"
          onClick={handleCompare}
          disabled={!player1.trim() || !player2.trim() || loading}
        >
          ⚔️ Compare
        </button>
      </div>

      {error && <div className="search-error">⚠️ {error}</div>}

      {loading && (
        <>
          <AgentProgress agents={[]} isLoading={true} />
          <LoadingSpinner text="Comparing players with AI agents..." />
        </>
      )}

      {/* Results */}
      {result && !loading && (
        <div className="compare-results animate-fade-in">
          {/* Side by side stats */}
          <div className="compare-columns">
            {renderPlayerColumn(result.player1_data, player1)}
            <div className="compare-divider" />
            {renderPlayerColumn(result.player2_data, player2)}
          </div>

          {/* Radar chart */}
          {radarData && (
            <div className="compare-chart glass-card">
              <h3 className="compare-chart-title">Performance Radar</h3>
              <div className="compare-chart-container">
                <Radar data={radarData} options={radarOptions} />
              </div>
            </div>
          )}

          {/* AI Comparison */}
          {result.ai_comparison && (
            <div className="compare-ai glass-card">
              <div className="compare-ai-header" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
                  <h3 className="compare-ai-title">AI Comparison Analysis</h3>
                  <span className="source-tag source-tag-ai">AI Multi-Agent Report</span>
                </div>
                {result.sources && result.sources.length > 0 && (
                  <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                    <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Data Sources:</span>
                    {result.sources.map((s, i) => (
                      <span key={i} className="badge badge-blue">{s}</span>
                    ))}
                  </div>
                )}
              </div>
              <div className="compare-ai-body">
                <ReactMarkdown>{result.ai_comparison}</ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
