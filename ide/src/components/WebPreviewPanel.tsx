import React, { useState } from 'react';
import { Globe, ExternalLink, Code2, RefreshCw } from 'lucide-react';
import { BuildResult } from '../types';

interface WebPreviewPanelProps {
  buildResult: BuildResult | null;
  onRefresh: () => void;
}

export const WebPreviewPanel: React.FC<WebPreviewPanelProps> = ({
  buildResult,
  onRefresh,
}) => {
  const [showCode, setShowCode] = useState(false);

  const fullHtml = buildResult?.html
    ? buildResult.html.replace(
        '<link rel="stylesheet" href="style.css">',
        `<style>${buildResult.css}</style>`
      )
    : '';

  const handleOpenNewTab = () => {
    if (!fullHtml) return;
    const blob = new Blob([fullHtml], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    window.open(url, '_blank');
  };

  return (
    <div className="ent-web-preview-container">
      <div className="ent-panel-toolbar">
        <div className="ent-panel-title">
          <Globe size={14} />
          <span>Web Preview: {buildResult?.title || 'Static Site'}</span>
        </div>

        <div className="ent-panel-actions">
          <button
            className="ent-mini-btn"
            onClick={onRefresh}
            title="Re-render Static Website"
          >
            <RefreshCw size={13} />
            <span>Refresh</span>
          </button>
          <button
            className="ent-mini-btn"
            onClick={() => setShowCode(!showCode)}
            title="Toggle Raw HTML/CSS Code"
          >
            <Code2 size={13} />
            <span>{showCode ? 'View Preview' : 'View Code'}</span>
          </button>
          <button
            className="ent-mini-btn"
            onClick={handleOpenNewTab}
            disabled={!buildResult?.html}
            title="Open in New Browser Tab"
          >
            <ExternalLink size={13} />
            <span>New Tab</span>
          </button>
        </div>
      </div>

      <div className="ent-preview-body">
        {buildResult ? (
          showCode ? (
            <div className="ent-raw-code-view">
              <h4>Generated HTML (Safe & Escaped)</h4>
              <pre>{buildResult.html}</pre>
              <h4>Generated CSS</h4>
              <pre>{buildResult.css}</pre>
            </div>
          ) : (
            <iframe
              title="ENT Static Website Preview"
              className="ent-preview-iframe"
              sandbox="allow-scripts"
              srcDoc={fullHtml}
            />
          )
        ) : (
          <div className="ent-preview-empty">
            Click <strong>Preview Web</strong> or run a program containing <code>page(...) [ ... ]</code> to render the website here.
          </div>
        )}
      </div>
    </div>
  );
};
