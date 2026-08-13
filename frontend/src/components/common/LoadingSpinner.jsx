import './LoadingSpinner.css';

export default function LoadingSpinner({ text = 'Loading...', size = 'md' }) {
  return (
    <div className={`spinner-container spinner-${size}`}>
      <div className="spinner-football">
        <div className="spinner-ball">⚽</div>
      </div>
      {text && <p className="spinner-text">{text}</p>}
    </div>
  );
}
