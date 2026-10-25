import React, { useRef, useState, useEffect } from 'react';
import { FileCode, Plus, FolderOpen, Download, RotateCcw, BookOpen, Edit2, Check, X } from 'lucide-react';

interface SidebarProps {
  currentFile: string;
  files: string[];
  renamingFile: string | null;
  onSelectFile: (fileName: string) => void;
  onNewFile: () => void;
  onImportFile: (fileName: string, content: string) => void;
  onExportFile: () => void;
  onResetFile: () => void;
  onStartRename: (fileName: string) => void;
  onConfirmRename: (oldName: string, newName: string) => void;
  onCancelRename: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentFile,
  files,
  renamingFile,
  onSelectFile,
  onNewFile,
  onImportFile,
  onExportFile,
  onResetFile,
  onStartRename,
  onConfirmRename,
  onCancelRename,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const renameInputRef = useRef<HTMLInputElement>(null);
  const [renameValue, setRenameValue] = useState<string>('');
  const [contextMenu, setContextMenu] = useState<{ x: number; y: number; file: string } | null>(null);

  // When entering rename mode, initialize input with current filename and select base name
  useEffect(() => {
    if (renamingFile) {
      setRenameValue(renamingFile);
      setTimeout(() => {
        if (renameInputRef.current) {
          renameInputRef.current.focus();
          const baseName = renamingFile.replace(/\.ent$/, '');
          renameInputRef.current.setSelectionRange(0, baseName.length);
        }
      }, 50);
    }
  }, [renamingFile]);

  // Global F2 shortcut to rename active file
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'F2' && !renamingFile && currentFile) {
        e.preventDefault();
        onStartRename(currentFile);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentFile, renamingFile, onStartRename]);

  // Close context menu on click outside
  useEffect(() => {
    const handleClickOutside = () => setContextMenu(null);
    window.addEventListener('click', handleClickOutside);
    return () => window.removeEventListener('click', handleClickOutside);
  }, []);

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

  const handleRenameSubmit = () => {
    if (!renamingFile) return;
    const trimmed = renameValue.trim();
    if (!trimmed || trimmed === renamingFile) {
      onCancelRename();
      return;
    }
    // Auto-append .ent if omitted
    const finalName = trimmed.endsWith('.ent') ? trimmed : `${trimmed}.ent`;
    onConfirmRename(renamingFile, finalName);
  };

  const handleRenameKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleRenameSubmit();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      onCancelRename();
    }
  };

  const handleContextMenu = (e: React.MouseEvent, file: string) => {
    e.preventDefault();
    setContextMenu({ x: e.clientX, y: e.clientY, file });
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
          <button
            className="ent-tool-btn"
            onClick={() => onStartRename(currentFile)}
            title="Rename active file (F2)"
          >
            <Edit2 size={14} />
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
          {files.map((file) => {
            const isRenaming = renamingFile === file;
            const isActive = currentFile === file;

            return (
              <div
                key={file}
                className={`ent-file-row ${isActive ? 'active' : ''}`}
                onContextMenu={(e) => handleContextMenu(e, file)}
              >
                {isRenaming ? (
                  <div className="ent-inline-rename">
                    <input
                      ref={renameInputRef}
                      type="text"
                      className="ent-rename-input"
                      value={renameValue}
                      onChange={(e) => setRenameValue(e.target.value)}
                      onKeyDown={handleRenameKeyDown}
                      onBlur={handleRenameSubmit}
                    />
                    <button
                      className="ent-rename-action-btn confirm"
                      onMouseDown={(e) => { e.preventDefault(); handleRenameSubmit(); }}
                      title="Confirm (Enter)"
                    >
                      <Check size={12} />
                    </button>
                    <button
                      className="ent-rename-action-btn cancel"
                      onMouseDown={(e) => { e.preventDefault(); onCancelRename(); }}
                      title="Cancel (Esc)"
                    >
                      <X size={12} />
                    </button>
                  </div>
                ) : (
                  <button
                    className="ent-file-item"
                    onClick={() => onSelectFile(file)}
                    title={file}
                  >
                    <FileCode size={15} className="file-icon" />
                    <span className="file-name">{file}</span>
                  </button>
                )}

                {!isRenaming && (
                  <div className="ent-file-actions">
                    <button
                      className="ent-file-action-icon"
                      onClick={(e) => {
                        e.stopPropagation();
                        onStartRename(file);
                      }}
                      title="Rename file (F2)"
                    >
                      <Edit2 size={12} />
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {contextMenu && (
        <div
          className="ent-context-menu"
          style={{ top: contextMenu.y, left: contextMenu.x }}
          onClick={(e) => e.stopPropagation()}
        >
          <button
            className="ent-context-item"
            onClick={() => {
              onStartRename(contextMenu.file);
              setContextMenu(null);
            }}
          >
            <Edit2 size={13} />
            <span>Rename File (F2)</span>
          </button>
          <button
            className="ent-context-item"
            onClick={() => {
              onExportFile();
              setContextMenu(null);
            }}
          >
            <Download size={13} />
            <span>Download</span>
          </button>
        </div>
      )}

      <div className="ent-sidebar-footer">
        <div className="ent-info-card">
          <h4>💡 Quick Tips</h4>
          <p>• Code must be inside <code>[ ... ]</code></p>
          <p>• Press <code>F2</code> to rename active file</p>
          <p>• Press <code>Ctrl+Enter</code> to execute</p>
        </div>
      </div>
    </aside>
  );
};
