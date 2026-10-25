import { RunResult, CheckResult, BuildResult, ExamplePrograms } from '../types';

const API_BASE = '/api';

export async function runCode(source: string): Promise<RunResult> {
  const res = await fetch(`${API_BASE}/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source }),
  });
  if (!res.ok) {
    throw new Error(`Server returned ${res.status}: ${res.statusText}`);
  }
  return res.json();
}

export async function checkCode(source: string): Promise<CheckResult> {
  const res = await fetch(`${API_BASE}/check`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source }),
  });
  if (!res.ok) {
    throw new Error(`Server returned ${res.status}: ${res.statusText}`);
  }
  return res.json();
}

export async function buildWebsite(source: string): Promise<BuildResult> {
  const res = await fetch(`${API_BASE}/build`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source }),
  });
  if (!res.ok) {
    throw new Error(`Server returned ${res.status}: ${res.statusText}`);
  }
  return res.json();
}

export async function getExamples(): Promise<ExamplePrograms> {
  const res = await fetch(`${API_BASE}/examples`);
  if (!res.ok) {
    throw new Error(`Server returned ${res.status}: ${res.statusText}`);
  }
  return res.json();
}
