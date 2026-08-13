import { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import './Sidebar.css';

const navItems = [
  { path: '/', label: 'Dashboard', icon: '📊' },
  { path: '/chat', label: 'AI Chat', icon: '💬' },
  { path: '/players', label: 'Player Search', icon: '🔍' },
  { path: '/compare', label: 'Comparison', icon: '⚔️' },
  { path: '/scout', label: 'AI Scout', icon: '🎯' },
  { path: '/settings', label: 'Settings', icon: '⚙️' },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  return (
    <>
      {/* Mobile overlay */}
      <div
        className={`sidebar-overlay ${collapsed ? '' : 'hidden'}`}
        onClick={() => setCollapsed(false)}
      />

      <aside className={`sidebar ${collapsed ? 'sidebar-collapsed' : ''}`}>
        {/* Brand */}
        <div className="sidebar-brand">
          <div className="sidebar-logo">⚽</div>
          {!collapsed && (
            <div className="sidebar-brand-text">
              <span className="sidebar-title gradient-text">Football AI</span>
              <span className="sidebar-subtitle">Intelligence System</span>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? 'sidebar-link-active' : ''}`
              }
              title={item.label}
            >
              <span className="sidebar-link-icon">{item.icon}</span>
              {!collapsed && (
                <span className="sidebar-link-label">{item.label}</span>
              )}
              {!collapsed && location.pathname === item.path && (
                <span className="sidebar-link-indicator" />
              )}
            </NavLink>
          ))}
        </nav>

        {/* Collapse toggle */}
        <button
          className="sidebar-toggle"
          onClick={() => setCollapsed(!collapsed)}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? '→' : '←'}
        </button>

        {/* Footer */}
        {!collapsed && (
          <div className="sidebar-footer">
            <div className="sidebar-footer-badge badge-green">
              Multi-Agent AI
            </div>
            <span className="sidebar-footer-version">v1.0.0</span>
          </div>
        )}
      </aside>
    </>
  );
}
