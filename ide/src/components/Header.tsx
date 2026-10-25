import React from 'react';
import { Play, CheckCircle, Globe, Sun, Moon, Loader2 } from 'lucide-react';

interface HeaderProps {
  onRun: () => void;
  onCheck: () => void;
  onBuild: () => void;
  isRunning: boolean;
  theme: 'vs-dark' | 'light';
  onToggleTheme: () => void;
  status: 'idle' | 'running' | 'success' | 'error';
  statusMessage?: string;
}

export const Header: React.FC<HeaderProps> = ({
  onRun,
  onCheck,
  onBuild,
  isRunning,
  theme,
  onToggleTheme,
  status,
  statusMessage,
}) => {
  return (
    <header className="ent-header">
      <div className="ent-header-left">
        <div className="ent-logo">
          <span className="ent-logo-icon">⚡</span>
          <span className="ent-logo-text">ENT Studio</span>
          <span className="ent-version-badge">v0.1.0</span>
        </div>

        <div className="ent-actions">
          <button
            className="ent-btn ent-btn-primary"
            onClick={onRun}
            disabled={isRunning}
            title="Execute ENT Code (Ctrl+Enter)"
          >
            {isRunning ? <Loader2 className="icon-spin" size={16} /> : <Play size={16} />}
            <span>Run</span>
          </button>

          <button
            className="ent-btn ent-btn-secondary"
            onClick={onCheck}
            disabled={isRunning}
            title="Validate ENT syntax without execution"
          >
            <CheckCircle size={16} />
            <span>Check</span>
          </button>

          <button
            className="ent-btn ent-btn-secondary"
            onClick={onBuild}
            disabled={isRunning}
            title="Build and preview static website"
          >
            <Globe size={16} />
            <span>Preview Web</span>
          </button>
        </div>
      </div>

      <div className="ent-header-right">
        {statusMessage && (
          <div className={`ent-status-badge status-${status}`}>
            {status === 'running' && <Loader2 className="icon-spin" size={14} />}
            <span>{statusMessage}</span>
          </div>
        )}

        <button
          className="ent-icon-btn"
          onClick={onToggleTheme}
          title={`Switch to ${theme === 'vs-dark' ? 'Light' : 'Dark'} Theme`}
        >
          {theme === 'vs-dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>
    </header>
  );
};
