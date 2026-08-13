import { useState } from 'react';
import api from '../api/client';
import PlayerCard from '../components/Player/PlayerCard';
import LoadingSpinner from '../components/common/LoadingSpinner';
import EmptyState from '../components/common/EmptyState';
import './PlayerSearch.css';

export default function PlayerSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [news, setNews] = useState([]);
  const [newsLoading, setNewsLoading] = useState(false);

  const handleSearch = async () => {
    const q = query.trim();
    if (!q) return;

    setError('');
    setLoading(true);
    setSelectedPlayer(null);
    setNews([]);

    try {
      const data = await api.searchPlayers(q);
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePlayerClick = async (player) => {
    setSelectedPlayer(player);
    setNewsLoading(true);
    try {
      const data = await api.getPlayerNews(player.name);
      setNews(data.news || []);
    } catch {
      setNews([]);
    } finally {
      setNewsLoading(false);
    }
  };

  return (
    <div className="player-search-page animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">
          <span className="gradient-text">Player Search</span>
        </h1>
        <p className="page-subtitle">
          Search for any football player using API-Football data
        </p>
      </div>

      {/* Search bar */}
      <div className="search-bar-container">
        <input
          type="text"
          className="input search-bar-input"
          placeholder="Search for a player (e.g. Haaland, Mbappe, Salah)..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          maxLength={200}
        />
        <button
          className="btn btn-primary"
          onClick={handleSearch}
          disabled={!query.trim() || loading}
        >
          {loading ? '⏳' : '🔍'} Search
        </button>
      </div>

      {error && (
        <div className="search-error">⚠️ {error}</div>
      )}

      {loading && <LoadingSpinner text="Searching players..." />}

      {/* Results */}
      {results && !loading && (
        <div className="search-results-section">
          <div className="results-header">
            <h2 className="results-title">
              Results for "{results.query}"
              <span className="results-meta">
                {results.total} players found • Season {results.season}
              </span>
            </h2>
            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
              {results.sources && results.sources.length > 0 ? (
                results.sources.map((s, i) => (
                  <span key={i} className="badge badge-blue">{s}</span>
                ))
              ) : (
                <span className="source-tag source-tag-api">Multi-Source</span>
              )}
            </div>
          </div>

          {results.players.length === 0 ? (
            <EmptyState
              icon="🔍"
              title="No players found"
              message={`No results for "${results.query}". Try a different name.`}
            />
          ) : (
            <div className="player-grid stagger-children">
              {results.players.map((player, i) => (
                <PlayerCard
                  key={`${player.id}-${i}`}
                  player={player}
                  onClick={() => handlePlayerClick(player)}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Player detail panel */}
      {selectedPlayer && (
        <div className="player-detail-panel glass-card animate-slide-right">
          <div className="detail-panel-header">
            <h2 className="detail-panel-title">{selectedPlayer.name}</h2>
            <button className="btn btn-ghost btn-sm" onClick={() => setSelectedPlayer(null)}>✕</button>
          </div>

          <div className="detail-stats-grid">
            {[
              { label: 'Goals', value: selectedPlayer.goals },
              { label: 'Assists', value: selectedPlayer.assists },
              { label: 'Appearances', value: selectedPlayer.appearances },
              { label: 'Minutes', value: selectedPlayer.minutes },
              { label: 'Rating', value: selectedPlayer.rating || '—' },
              { label: 'Shots on Target', value: selectedPlayer.shots_on_target },
              { label: 'Dribbles', value: selectedPlayer.dribbles_success },
              { label: 'Tackles', value: selectedPlayer.tackles_total },
              { label: 'Yellow Cards', value: selectedPlayer.yellow_cards },
              { label: 'Red Cards', value: selectedPlayer.red_cards },
              { label: 'Pass Accuracy', value: selectedPlayer.passes_accuracy || '—' },
              { label: 'Season', value: selectedPlayer.season },
            ].map((s) => (
              <div key={s.label} className="detail-stat-item">
                <span className="detail-stat-label">{s.label}</span>
                <span className="detail-stat-value">{s.value ?? 0}</span>
              </div>
            ))}
          </div>

          {/* News */}
          <div className="detail-news-section">
            <h3 className="detail-news-title">
              Recent News
              <span className="source-tag source-tag-web">Web Research</span>
            </h3>
            {newsLoading ? (
              <LoadingSpinner text="Fetching news..." size="sm" />
            ) : news.length > 0 ? (
              <div className="detail-news-list">
                {news.map((item, i) => (
                  <a key={i} href={item.url} target="_blank" rel="noopener noreferrer" className="detail-news-item">
                    <span className="news-item-title">{item.title}</span>
                    <span className="news-item-content">{item.content?.slice(0, 120)}...</span>
                  </a>
                ))}
              </div>
            ) : (
              <p className="detail-news-empty">No recent news found.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
