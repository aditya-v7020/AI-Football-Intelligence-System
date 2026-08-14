import { useState, useEffect } from 'react';
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
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  // Auto-close mobile sidebar when navigating to a new route
  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  return (
    <>
      {/* Mobile Header Bar — visible only on screens <= 768px */}
      <header className="mobile-header">
        <div className="mobile-header-brand">
          <span className="mobile-header-logo">⚽</span>
          <span className="mobile-header-title gradient-text">Football AI</span>
        </div>
        <button
          className="mobile-menu-toggle"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
          aria-expanded={mobileOpen}
        >
          {mobileOpen ? '✕' : '☰'}
        </button>
      </header>

      {/* Mobile Backdrop Overlay */}
      {mobileOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setMobileOpen(false)}
          aria-hidden="true"
        />
      )}

      <aside className={`sidebar ${collapsed ? 'sidebar-collapsed' : ''} ${mobileOpen ? 'mobile-open' : ''}`}>
        {/* Brand */}
        <div className="sidebar-brand">
          <div className="sidebar-logo">⚽</div>
          {(!collapsed || mobileOpen) && (
            <div className="sidebar-brand-text">
              <span className="sidebar-title gradient-text">Football AI</span>
              <span className="sidebar-subtitle">Intelligence System</span>
            </div>
          )}
          {mobileOpen && (
            <button
              className="mobile-sidebar-close"
              onClick={() => setMobileOpen(false)}
              aria-label="Close menu"
            >
              ✕
            </button>
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
              onClick={() => setMobileOpen(false)}
            >
              <span className="sidebar-link-icon">{item.icon}</span>
              {(!collapsed || mobileOpen) && (
                <span className="sidebar-link-label">{item.label}</span>
              )}
              {(!collapsed || mobileOpen) && location.pathname === item.path && (
                <span className="sidebar-link-indicator" />
              )}
            </NavLink>
          ))}
        </nav>

        {/* Collapse toggle (desktop only) */}
        <button
          className="sidebar-toggle"
          onClick={() => setCollapsed(!collapsed)}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? '→' : '←'}
        </button>

        {/* Footer */}
        {(!collapsed || mobileOpen) && (
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
