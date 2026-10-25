import React, { useState, useEffect, useRef } from 'react';
import Editor, { Monaco } from '@monaco-editor/react';
import type { editor as MonacoEditorType } from 'monaco-editor';
import { Terminal, Globe, AlertCircle } from 'lucide-react';

import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { ConsolePanel } from './components/ConsolePanel';
import { WebPreviewPanel } from './components/WebPreviewPanel';
import { DiagnosticsPanel } from './components/DiagnosticsPanel';

import { registerEntLanguage, ENT_LANGUAGE_ID } from './editor/entLanguage';
import { runCode, checkCode, buildWebsite, getExamples, renameFile } from './services/api';
import { RunResult, BuildResult, EntError } from './types';
import './App.css';

const DEFAULT_FILES: Record<string, string> = {
  'hello.ent': '[\n    say("Hello, World!")\n]',
  'variables.ent': '[\n    remember(name = "ENT")\n    remember(version = "0.1.0")\n\n    say("Welcome to " + name)\n    say("Version: " + version)\n]',
  'math.ent': '[\n    say(2 + 2 - 9 + 3)\n]',
  'conditions.ent': '[\n    remember(age = 20)\n\n    if (age >= 18) [\n        say("Adult")\n    ] otherwise [\n        say("Minor")\n    ]\n]',
  'loops.ent': '[\n    repeat (3 as i) [\n        say("Repeat index: " + i)\n    ]\n\n    remember(count = 0)\n    while (count < 3) [\n        say("While count: " + count)\n        count = count + 1\n    ]\n]',
  'functions.ent': '[\n    function add(a, b) [\n        give a + b\n    ]\n\n    remember(result = add(10, 25))\n    say("10 + 25 = " + result)\n]',
  'website.ent': '[\n    page(title = "Welcome to ENT Programming") [\n        heading("Build Websites with Simple English", level = 1)\n        paragraph("ENT is a beginner-friendly, English-readable programming language designed for everyone.")\n\n        section() [\n            heading("Why ENT?", level = 2)\n            paragraph("Traditional programming languages require memorizing complex symbols and curly braces. ENT keeps everything readable and intuitive.")\n            button("Get Started", onclick = "alert(\'Welcome to ENT!\')")\n            link("Read the Docs", url = "https://github.com/debabrata/ent-programming")\n        ]\n    ]\n]',
};

export const App: React.FC = () => {
  const [theme, setTheme] = useState<'vs-dark' | 'light'>('vs-dark');
  const [files, setFiles] = useState<Record<string, string>>(DEFAULT_FILES);
  const [currentFile, setCurrentFile] = useState<string>('hello.ent');
  const [code, setCode] = useState<string>(DEFAULT_FILES['hello.ent']);
  const [renamingFile, setRenamingFile] = useState<string | null>(null);

  const [activeTab, setActiveTab] = useState<'console' | 'preview' | 'diagnostics'>('console');
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [status, setStatus] = useState<'idle' | 'running' | 'success' | 'error'>('idle');
  const [statusMessage, setStatusMessage] = useState<string>('Ready');

  const [runResult, setRunResult] = useState<RunResult | null>(null);
  const [buildResult, setBuildResult] = useState<BuildResult | null>(null);
  const [currentError, setCurrentError] = useState<EntError | null>(null);

  const editorRef = useRef<MonacoEditorType.IStandaloneCodeEditor | null>(null);
  const monacoRef = useRef<Monaco | null>(null);

  // Sync theme with document attribute
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme === 'vs-dark' ? 'dark' : 'light');
  }, [theme]);

  // Load examples from backend if available
  useEffect(() => {
    getExamples()
      .then((serverExamples) => {
        if (Object.keys(serverExamples).length > 0) {
          setFiles((prev) => ({ ...prev, ...serverExamples }));
        }
      })
      .catch(() => {
        // Fallback to local default files
      });
  }, []);

  // Update editor markers for errors
  const updateEditorMarkers = (error: EntError | null) => {
    if (!monacoRef.current || !editorRef.current) return;
    const model = editorRef.current.getModel();
    if (!model) return;

    if (!error) {
      monacoRef.current.editor.setModelMarkers(model, 'ent', []);
      return;
    }

    const marker: MonacoEditorType.IMarkerData = {
      severity: monacoRef.current.MarkerSeverity.Error,
      message: `${error.message}${error.suggestion ? `\nTip: ${error.suggestion}` : ''}`,
      startLineNumber: error.line,
      startColumn: error.column,
      endLineNumber: error.line,
      endColumn: error.column + 5,
    };
    monacoRef.current.editor.setModelMarkers(model, 'ent', [marker]);
  };

  const handleEditorDidMount = (editor: MonacoEditorType.IStandaloneCodeEditor, monaco: Monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;

    registerEntLanguage(monaco);

    // Keyboard shortcut: Ctrl+Enter / Cmd+Enter to Run
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      handleRun();
    });
  };

  const handleRun = async () => {
    if (isRunning) return;
    setIsRunning(true);
    setStatus('running');
    setStatusMessage('Running...');
    setCurrentError(null);
    updateEditorMarkers(null);

    try {
      const result = await runCode(code);
      setRunResult(result);

      if (result.success) {
        setStatus('success');
        setStatusMessage(`Done (${result.steps} steps)`);
        setActiveTab('console');

        // If code defines a page, also trigger static build for live preview
        if (code.includes('page(')) {
          try {
            const buildRes = await buildWebsite(code);
            setBuildResult(buildRes);
          } catch {
            // Ignore preview build failure during normal run
          }
        }
      } else if (result.error) {
        setStatus('error');
        setStatusMessage('Runtime Error');
        setCurrentError(result.error);
        updateEditorMarkers(result.error);
        setActiveTab('diagnostics');
      }
    } catch (err: any) {
      setStatus('error');
      setStatusMessage('Connection Failed');
      const connectionError: EntError = {
        category: 'Network Error',
        message: err.message || 'Could not communicate with the local ENT backend service.',
        file: currentFile,
        line: 1,
        column: 1,
        suggestion: 'Make sure the ENT execution server is running at http://127.0.0.1:8000',
        formatted: 'Failed to connect to backend execution engine.',
      };
      setCurrentError(connectionError);
      setActiveTab('diagnostics');
    } finally {
      setIsRunning(false);
    }
  };

  const handleCheck = async () => {
    if (isRunning) return;
    setIsRunning(true);
    setStatus('running');
    setStatusMessage('Validating...');
    setCurrentError(null);
    updateEditorMarkers(null);

    try {
      const result = await checkCode(code);
      if (result.valid) {
        setStatus('success');
        setStatusMessage('Syntax Valid');
        setActiveTab('console');
      } else if (result.error) {
        setStatus('error');
        setStatusMessage('Syntax Error');
        setCurrentError(result.error);
        updateEditorMarkers(result.error);
        setActiveTab('diagnostics');
      }
    } catch (err: any) {
      setStatus('error');
      setStatusMessage('Check Failed');
    } finally {
      setIsRunning(false);
    }
  };

  const handleBuild = async () => {
    if (isRunning) return;
    setIsRunning(true);
    setStatus('running');
    setStatusMessage('Building Website...');
    setCurrentError(null);
    updateEditorMarkers(null);

    try {
      const result = await buildWebsite(code);
      setBuildResult(result);
      if (result.success) {
        setStatus('success');
        setStatusMessage('Website Ready');
        setActiveTab('preview');
      } else if (result.error) {
        setStatus('error');
        setStatusMessage('Build Error');
        setCurrentError(result.error);
        updateEditorMarkers(result.error);
        setActiveTab('diagnostics');
      }
    } catch (err: any) {
      setStatus('error');
      setStatusMessage('Build Failed');
    } finally {
      setIsRunning(false);
    }
  };

  const handleSelectFile = (fileName: string) => {
    // Save current file
    setFiles((prev) => ({ ...prev, [currentFile]: code }));
    setCurrentFile(fileName);
    setCode(files[fileName] || '');
    setCurrentError(null);
    updateEditorMarkers(null);
  };

  const handleNewFile = () => {
    const baseName = 'untitled';
    let count = 1;
    let newName = `${baseName}.ent`;
    while (files[newName]) {
      count++;
      newName = `${baseName}_${count}.ent`;
    }

    const template = '[\n    say("Hello from new file!")\n]';
    setFiles((prev) => ({ ...prev, [newName]: template }));
    setCurrentFile(newName);
    setCode(template);
  };

  const handleImportFile = (fileName: string, content: string) => {
    setFiles((prev) => ({ ...prev, [fileName]: content }));
    setCurrentFile(fileName);
    setCode(content);
  };

  const handleExportFile = () => {
    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = currentFile;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleResetFile = () => {
    const original = DEFAULT_FILES[currentFile];
    if (original) {
      setCode(original);
      setFiles((prev) => ({ ...prev, [currentFile]: original }));
    }
  };

  const handleStartRename = (fileName: string) => {
    setRenamingFile(fileName);
  };

  const handleCancelRename = () => {
    setRenamingFile(null);
  };

  const handleConfirmRename = async (oldName: string, newName: string) => {
    setRenamingFile(null);
    if (oldName === newName) return;

    // Check collision in frontend files state
    if (files[newName] && newName.toLowerCase() !== oldName.toLowerCase()) {
      setStatus('error');
      setStatusMessage(`File '${newName}' already exists`);
      setCurrentError({
        category: 'File Error',
        message: `A file named '${newName}' already exists. Overwriting is not permitted.`,
        file: oldName,
        line: 1,
        column: 1,
        suggestion: 'Choose a distinct filename.',
        formatted: `[File Error] Destination file '${newName}' already exists.`,
      });
      setActiveTab('diagnostics');
      return;
    }

    try {
      // Call backend rename endpoint
      await renameFile(oldName, newName);

      // Preserve unsaved code if the renamed file is the active editor file
      const currentContent = oldName === currentFile ? code : (files[oldName] || '');

      setFiles((prev) => {
        const updated = { ...prev };
        delete updated[oldName];
        updated[newName] = currentContent;
        return updated;
      });

      if (currentFile === oldName) {
        setCurrentFile(newName);
      }

      setStatus('success');
      setStatusMessage(`Renamed to ${newName}`);
    } catch (err: any) {
      setStatus('error');
      setStatusMessage('Rename Failed');
      setCurrentError({
        category: 'Rename Error',
        message: err.message || `Failed to rename '${oldName}' to '${newName}'.`,
        file: oldName,
        line: 1,
        column: 1,
        suggestion: 'Ensure the new filename is valid, does not contain path separators, and ends with .ent',
        formatted: `[Rename Error] ${err.message || 'Failed to rename file.'}`,
      });
      setActiveTab('diagnostics');
    }
  };

  return (
    <div className="ent-app">
      <Header
        onRun={handleRun}
        onCheck={handleCheck}
        onBuild={handleBuild}
        isRunning={isRunning}
        theme={theme}
        onToggleTheme={() => setTheme(theme === 'vs-dark' ? 'light' : 'vs-dark')}
        status={status}
        statusMessage={statusMessage}
      />

      <div className="ent-workspace">
        <Sidebar
          currentFile={currentFile}
          files={Object.keys(files)}
          renamingFile={renamingFile}
          onSelectFile={handleSelectFile}
          onNewFile={handleNewFile}
          onImportFile={handleImportFile}
          onExportFile={handleExportFile}
          onResetFile={handleResetFile}
          onStartRename={handleStartRename}
          onConfirmRename={handleConfirmRename}
          onCancelRename={handleCancelRename}
        />

        <main className="ent-main-container">
          <div className="ent-editor-pane">
            <Editor
              height="100%"
              language={ENT_LANGUAGE_ID}
              theme={theme}
              value={code}
              onChange={(value) => setCode(value || '')}
              onMount={handleEditorDidMount}
              options={{
                fontSize: 14,
                fontFamily: "'JetBrains Mono', Consolas, 'Fira Code', monospace",
                lineNumbers: 'on',
                renderWhitespace: 'selection',
                bracketPairColorization: { enabled: true },
                automaticLayout: true,
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                tabSize: 4,
                insertSpaces: true,
              }}
            />
          </div>

          <div className="ent-bottom-pane">
            <div className="ent-tab-bar">
              <button
                className={`ent-tab ${activeTab === 'console' ? 'active' : ''}`}
                onClick={() => setActiveTab('console')}
              >
                <Terminal size={14} />
                <span>Console</span>
              </button>

              <button
                className={`ent-tab ${activeTab === 'preview' ? 'active' : ''}`}
                onClick={() => setActiveTab('preview')}
              >
                <Globe size={14} />
                <span>Web Preview</span>
              </button>

              <button
                className={`ent-tab ${activeTab === 'diagnostics' ? 'active' : ''}`}
                onClick={() => setActiveTab('diagnostics')}
              >
                <AlertCircle size={14} />
                <span>Diagnostics</span>
                {currentError && <span className="ent-badge">1</span>}
              </button>
            </div>

            <div className="ent-panel-content">
              {activeTab === 'console' && (
                <ConsolePanel
                  outputLines={runResult?.output_lines || []}
                  steps={runResult?.steps || 0}
                  onClear={() => setRunResult(null)}
                />
              )}

              {activeTab === 'preview' && (
                <WebPreviewPanel
                  buildResult={buildResult}
                  onRefresh={handleBuild}
                />
              )}

              {activeTab === 'diagnostics' && (
                <DiagnosticsPanel error={currentError} />
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default App;
