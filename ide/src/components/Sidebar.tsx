import React, { useRef } from 'react';
import { FileCode, Plus, FolderOpen, Download, RotateCcw, BookOpen } from 'lucide-react';

interface SidebarProps {
  currentFile: string;
  files: string[];
  onSelectFile: (fileName: string) => void;
  onNewFile: () => void;
  onImportFile: (fileName: string, content: string) => void;
  onExportFile: () => void;
  onResetFile: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentFile,
  files,
  onSelectFile,
  onNewFile,
  onImportFile,
  onExportFile,
  onResetFile,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      onImportFile(file.name, content);
    };
    reader.readAsText(file);
    e.target.value = '';
  };

  return (
    <aside className="ent-sidebar">
      <div className="ent-sidebar-section">
        <div className="ent-sidebar-title">
          <BookOpen size={16} />
          <span>Explorer & Examples</span>
        </div>

        <div className="ent-sidebar-toolbar">
          <button className="ent-tool-btn" onClick={onNewFile} title="New .ent file">
            <Plus size={15} />
          </button>
          <button
            className="ent-tool-btn"
            onClick={() => fileInputRef.current?.click()}
            title="Open / Import .ent file"
          >
            <FolderOpen size={15} />
          </button>
          <button className="ent-tool-btn" onClick={onExportFile} title="Download .ent file">
            <Download size={15} />
          </button>
          <button className="ent-tool-btn" onClick={onResetFile} title="Reset example to original">
            <RotateCcw size={15} />
          </button>

          <input
            ref={fileInputRef}
            type="file"
            accept=".ent"
            style={{ display: 'none' }}
            onChange={handleFileChange}
          />
        </div>

        <div className="ent-file-list">
          {files.map((file) => (
            <button
              key={file}
              className={`ent-file-item ${file === currentFile ? 'active' : ''}`}
              onClick={() => onSelectFile(file)}
            >
              <FileCode size={15} className="file-icon" />
              <span className="file-name">{file}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="ent-sidebar-footer">
        <div className="ent-info-card">
          <h4>💡 Quick Tips</h4>
          <p>• Code must be inside <code>[ ... ]</code></p>
          <p>• Curly braces <code>{`{ }`}</code> are forbidden</p>
          <p>• Press <code>Ctrl+Enter</code> to execute</p>
        </div>
      </div>
    </aside>
  );
};
