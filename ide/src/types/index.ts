export interface EntError {
  category: string;
  message: string;
  file: string;
  line: number;
  column: number;
  source_line?: string;
  suggestion?: string;
  formatted: string;
}

export interface RunResult {
  success: boolean;
  output: string;
  output_lines: string[];
  steps: number;
  error?: EntError | null;
}

export interface CheckResult {
  valid: boolean;
  error?: EntError | null;
}

export interface BuildResult {
  success: boolean;
  title: string;
  html: string;
  css: string;
  error?: EntError | null;
}

export interface ExamplePrograms {
  [fileName: string]: string;
}
