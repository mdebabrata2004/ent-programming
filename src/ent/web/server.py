"""
FastAPI local execution and IDE backend service for ENT Studio.
Binds to localhost by default, providing safe AST parsing, execution, and web generation endpoints.
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from ent import __version__, __language__
from ent.lexer import Lexer
from ent.parser import Parser
from ent.interpreter import run_ent
from ent.runtime import RuntimeLimits
from ent.errors import EntError
from ent.web.builder import build_website_from_source

app = FastAPI(
    title="ENT Studio Backend API",
    version=__version__,
    description="Local execution and validation engine for ENT Studio IDE.",
)

# CORS configuration for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CodePayload(BaseModel):
    source: str = Field(..., max_length=1_000_000, description="ENT source code")
    max_steps: Optional[int] = Field(100_000, ge=1, le=1_000_000, description="Max execution steps")


class RunResponse(BaseModel):
    success: bool
    output: str
    output_lines: List[str]
    steps: int
    error: Optional[Dict[str, Any]] = None


class CheckResponse(BaseModel):
    valid: bool
    error: Optional[Dict[str, Any]] = None


class BuildResponse(BaseModel):
    success: bool
    title: str
    html: str
    css: str
    error: Optional[Dict[str, Any]] = None


EXAMPLES_DIR = Path(__file__).resolve().parent.parent.parent.parent / "examples"
IDE_DIST_DIR = Path(__file__).resolve().parent.parent.parent.parent / "ide" / "dist"


@app.get("/api/version")
def get_version() -> Dict[str, str]:
    return {"language": __language__, "version": __version__}


@app.get("/api/examples")
def list_examples() -> Dict[str, str]:
    examples: Dict[str, str] = {}
    if EXAMPLES_DIR.exists():
        for file in sorted(EXAMPLES_DIR.glob("*.ent")):
            try:
                examples[file.name] = file.read_text(encoding="utf-8")
            except Exception:
                pass
    return examples


@app.post("/api/run", response_model=RunResponse)
def run_code(payload: CodePayload) -> RunResponse:
    limits = RuntimeLimits(max_steps=payload.max_steps or 100_000)
    result = run_ent(payload.source, file_path="<studio>", limits=limits)

    error_dict = result.error.to_dict() if result.error else None
    return RunResponse(
        success=result.success,
        output=result.output,
        output_lines=result.output_lines,
        steps=result.steps,
        error=error_dict,
    )


@app.post("/api/check", response_model=CheckResponse)
def check_code(payload: CodePayload) -> CheckResponse:
    try:
        lexer = Lexer(payload.source, file_path="<studio>")
        tokens = lexer.tokenize()
        parser = Parser(tokens, source=payload.source, file_path="<studio>")
        parser.parse()
        return CheckResponse(valid=True, error=None)
    except EntError as err:
        return CheckResponse(valid=False, error=err.to_dict())


@app.post("/api/build", response_model=BuildResponse)
def build_code(payload: CodePayload) -> BuildResponse:
    try:
        generated = build_website_from_source(payload.source, file_path="<studio>")
        return BuildResponse(
            success=True,
            title=generated.title,
            html=generated.html,
            css=generated.css,
            error=None,
        )
    except EntError as err:
        return BuildResponse(
            success=False,
            title="",
            html="",
            css="",
            error=err.to_dict(),
        )


if IDE_DIST_DIR.exists() and (IDE_DIST_DIR / "index.html").exists():
    if (IDE_DIST_DIR / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(IDE_DIST_DIR / "assets")), name="assets")

    @app.get("/", response_class=HTMLResponse)
    def serve_ide_index():
        return (IDE_DIST_DIR / "index.html").read_text(encoding="utf-8")


def start_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Entry point to launch the local execution server."""
    import uvicorn
    uvicorn.run("ent.web.server:app", host=host, port=port, log_level="info")


if __name__ == "__main__":
    start_server()
