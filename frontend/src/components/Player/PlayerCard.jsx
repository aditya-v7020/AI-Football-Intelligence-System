import './PlayerCard.css';

export default function PlayerCard({ player, onClick = null }) {
  return (
    <div className="player-card glass-card" onClick={onClick}>
      <div className="player-card-header">
        <div className="player-card-photo-wrap">
          {player.photo ? (
            <img src={player.photo} alt={player.name} className="player-card-photo" />
          ) : (
            <div className="player-card-photo-placeholder">⚽</div>
          )}
        </div>
        <div className="player-card-badge-row">
          <span className="badge badge-green">{player.position || 'N/A'}</span>
          <span className="source-tag source-tag-api">{player.source || 'API Data'}</span>
        </div>
      </div>

      <div className="player-card-body">
        <h3 className="player-card-name">{player.name}</h3>
        <div className="player-card-team">
          {player.team_logo && (
            <img src={player.team_logo} alt="" className="player-card-team-logo" />
          )}
          <span>{player.team || 'Unknown'}</span>
        </div>
        <p className="player-card-league">{player.league || 'Unknown'}</p>

        <div className="player-card-meta">
          <div className="player-card-meta-item">
            <span className="meta-label">Age</span>
            <span className="meta-value">{player.age || '—'}</span>
          </div>
          <div className="player-card-meta-item">
            <span className="meta-label">Nationality</span>
            <span className="meta-value">{player.nationality || '—'}</span>
          </div>
        </div>

        <div className="player-card-stats">
          <div className="stat-item">
            <span className="stat-value">{player.goals ?? 0}</span>
            <span className="stat-label">Goals</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{player.assists ?? 0}</span>
            <span className="stat-label">Assists</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{player.appearances ?? 0}</span>
            <span className="stat-label">Apps</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{player.rating || '—'}</span>
            <span className="stat-label">Rating</span>
          </div>
        </div>
      </div>
    </div>
  );
}
