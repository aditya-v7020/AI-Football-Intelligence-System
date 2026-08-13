import './EmptyState.css';

export default function EmptyState({
  icon = '🔍',
  title = 'Nothing here yet',
  message = '',
  action = null,
  actionLabel = '',
  onAction = null,
}) {
  return (
    <div className="empty-state">
      <div className="empty-state-icon">{icon}</div>
      <h3 className="empty-state-title">{title}</h3>
      {message && <p className="empty-state-message">{message}</p>}
      {action && (
        <button className="btn btn-primary" onClick={onAction}>
          {actionLabel}
        </button>
      )}
    </div>
  );
}
