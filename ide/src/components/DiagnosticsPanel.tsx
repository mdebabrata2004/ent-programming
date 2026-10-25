import React from 'react';
import { AlertCircle, Info } from 'lucide-react';
import { EntError } from '../types';

interface DiagnosticsPanelProps {
  error: EntError | null;
}

export const DiagnosticsPanel: React.FC<DiagnosticsPanelProps> = ({ error }) => {
  if (!error) {
    return (
      <div className="ent-diagnostics-container">
        <div className="ent-diagnostics-empty">
          <Info size={16} />
          <span>No errors detected. Code is valid!</span>
        </div>
      </div>
    );
  }

  return (
    <div className="ent-diagnostics-container error-state">
      <div className="ent-error-header">
        <AlertCircle size={18} className="error-icon" />
        <span className="error-category">[{error.category}]</span>
        <span className="error-location">Line {error.line}, Column {error.column}</span>
      </div>

      <div className="ent-error-message">{error.message}</div>

      {error.source_line && (
        <div className="ent-error-source-snippet">
          <pre>{error.source_line}</pre>
          <pre className="pointer">
            {' '.repeat(Math.max(0, error.column - 1)) + '^'}
          </pre>
        </div>
      )}

      {error.suggestion && (
        <div className="ent-error-suggestion">
          <strong>💡 Beginner Tip:</strong> {error.suggestion}
        </div>
      )}
    </div>
  );
};
