import React from 'react';
import { Terminal, Trash2 } from 'lucide-react';

interface ConsolePanelProps {
  outputLines: string[];
  steps: number;
  onClear: () => void;
}

export const ConsolePanel: React.FC<ConsolePanelProps> = ({
  outputLines,
  steps,
  onClear,
}) => {
  return (
    <div className="ent-console-container">
      <div className="ent-panel-toolbar">
        <div className="ent-panel-title">
          <Terminal size={14} />
          <span>Output Console</span>
          {steps > 0 && <span className="ent-step-counter">({steps} steps)</span>}
        </div>
        <button className="ent-mini-btn" onClick={onClear} title="Clear Console">
          <Trash2 size={13} />
          <span>Clear</span>
        </button>
      </div>

      <div className="ent-console-output">
        {outputLines.length > 0 ? (
          outputLines.map((line, idx) => (
            <div key={idx} className="ent-console-line">
              <span className="line-prefix">&gt;</span>
              <span className="line-text">{line}</span>
            </div>
          ))
        ) : (
          <div className="ent-console-empty">
            Program output will appear here after clicking <strong>Run</strong> (Ctrl+Enter).
          </div>
        )}
      </div>
    </div>
  );
};
