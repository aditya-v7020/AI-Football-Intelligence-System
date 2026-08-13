import './AgentProgress.css';

const AGENTS = [
  { key: 'player_agent', label: 'Player Agent', icon: '⚽', description: 'Fetching API-Football data' },
  { key: 'research_agent', label: 'Research Agent', icon: '🔎', description: 'Web research via Tavily' },
  { key: 'analysis_agent', label: 'Analysis Agent', icon: '📊', description: 'AI-powered analysis' },
  { key: 'final_agent', label: 'Final Agent', icon: '✨', description: 'Generating response' },
];

export default function AgentProgress({ agents = [], isLoading = false }) {
  const getAgentStatus = (key) => {
    const agent = agents.find((a) => a.agent === key);
    return agent?.status || (isLoading ? 'pending' : 'idle');
  };

  return (
    <div className="agent-progress">
      <div className="agent-progress-header">
        <span className="agent-progress-label">Multi-Agent Pipeline</span>
        {isLoading && <span className="agent-progress-status badge badge-green">Processing</span>}
      </div>
      <div className="agent-pipeline">
        {AGENTS.map((agent, idx) => {
          const status = getAgentStatus(agent.key);
          return (
            <div key={agent.key} className="agent-step-wrapper">
              <div className={`agent-step agent-step-${status}`}>
                <div className="agent-step-icon-wrap">
                  <span className="agent-step-icon">{agent.icon}</span>
                  {status === 'running' && <div className="agent-step-pulse" />}
                </div>
                <div className="agent-step-info">
                  <span className="agent-step-name">{agent.label}</span>
                  <span className="agent-step-desc">{agent.description}</span>
                </div>
                <div className={`agent-step-status-dot status-${status}`} />
              </div>
              {idx < AGENTS.length - 1 && (
                <div className={`agent-connector ${status === 'completed' ? 'connector-active' : ''}`}>
                  <div className="connector-line" />
                  <span className="connector-arrow">→</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
