import ReactMarkdown from 'react-markdown';
import './ChatMessage.css';

export default function ChatMessage({ role, content, sources = [] }) {
  const isUser = role === 'user';

  return (
    <div className={`chat-message ${isUser ? 'chat-message-user' : 'chat-message-ai'} animate-fade-in`}>
      <div className="chat-message-avatar">
        {isUser ? '👤' : '🤖'}
      </div>
      <div className="chat-message-content">
        <div className="chat-message-header">
          <span className="chat-message-sender">
            {isUser ? 'You' : 'Football AI'}
          </span>
          {!isUser && (
            <span className="source-tag source-tag-ai">AI Response</span>
          )}
        </div>
        <div className="chat-message-body">
          {isUser ? (
            <p>{content}</p>
          ) : (
            <ReactMarkdown>{content}</ReactMarkdown>
          )}
        </div>
        {sources.length > 0 && (
          <div className="chat-message-sources" style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: '8px' }}>
            <span className="chat-sources-label" style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Data Sources:</span>
            {sources.map((src, i) => (
              typeof src === 'string' ? (
                <span key={i} className="badge badge-blue" style={{ fontSize: '0.75rem' }}>{src}</span>
              ) : (
                <a key={i} href={src.url} target="_blank" rel="noopener noreferrer" className="chat-source-link">
                  {src.title || src.url}
                </a>
              )
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
