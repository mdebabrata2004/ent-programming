"""
FastAPI local execution and IDE backend service for ENT Studio.
Binds to localhost by default, providing safe AST parsing, execution, and web generation endpoints.
"""

from __future__ import annotations
import os
import re
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request, status
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


def get_workspace_dir() -> Path:
    """Configured workspace root for ENT files."""
    env_dir = os.environ.get("ENT_WORKSPACE_DIR")
    if env_dir:
        p = Path(env_dir).resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p
    return (Path(__file__).resolve().parent.parent.parent.parent / "examples").resolve()


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


class RenameFilePayload(BaseModel):
    old_name: str = Field(..., min_length=1, max_length=255, description="Current file name")
    new_name: str = Field(..., min_length=1, max_length=255, description="New file name")


class RenameFileResponse(BaseModel):
    success: bool
    old_name: str
    new_name: str
    message: str


EXAMPLES_DIR = Path(__file__).resolve().parent.parent.parent.parent / "examples"
IDE_DIST_DIR = Path(__file__).resolve().parent.parent.parent.parent / "ide" / "dist"


@app.get("/api/version")
def get_version() -> Dict[str, str]:
    return {"language": __language__, "version": __version__}


@app.get("/api/examples")
def list_examples() -> Dict[str, str]:
    workspace = get_workspace_dir()
    examples: Dict[str, str] = {}
    if workspace.exists():
        for file in sorted(workspace.glob("*.ent")):
            try:
                examples[file.name] = file.read_text(encoding="utf-8")
            except Exception:
                pass
    return examples


def validate_filename(name: str) -> None:
    """Validates filename against path traversal, invalid characters, and empty names."""
    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filename cannot be empty.")

    # Check for path traversal characters first
    if ".." in name or "/" in name or "\\" in name or "\0" in name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Path traversal attempt detected. Filename must not contain path separators or '..'.",
        )

    # Must not start or end with dot or space
    if name.startswith(".") or name.endswith(".") or name.startswith(" ") or name.endswith(" "):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename cannot start or end with a space or dot.",
        )

    # Check for valid characters
    if not re.match(r"^[a-zA-Z0-9_\-\. ]+$", name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Filename '{name}' contains invalid characters. Use only letters, numbers, spaces, dashes, dots, and underscores.",
        )

    # Extension check: ENT only supports .ent files in the workspace
    if not name.endswith(".ent"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension in '{name}'. Only '.ent' files are supported.",
        )


@app.post("/api/files/rename", response_model=RenameFileResponse)
def rename_file(payload: RenameFilePayload) -> RenameFileResponse:
    workspace = get_workspace_dir().resolve()
    old_name = payload.old_name
    new_name = payload.new_name

    validate_filename(old_name)
    validate_filename(new_name)

    src_path = (workspace / old_name).resolve()
    dst_path = (workspace / new_name).resolve()

    # Enforce project root boundary
    try:
        src_path.relative_to(workspace)
        dst_path.relative_to(workspace)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Access outside project root is forbidden.",
        )

    if not src_path.exists() or not src_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source file '{old_name}' not found.",
        )

    # Check if this is a case-only rename
    is_case_only = False
    if dst_path.exists():
        try:
            if src_path.samefile(dst_path):
                is_case_only = True
        except Exception:
            pass

        if not is_case_only:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Destination file '{new_name}' already exists. Overwriting is not permitted.",
            )

    try:
        if is_case_only and os.name == "nt":
            # Two-step rename for Windows case-insensitive filesystem
            tmp_path = workspace / f".__ent_rename_tmp_{uuid.uuid4().hex}.ent"
            src_path.rename(tmp_path)
            tmp_path.rename(dst_path)
        else:
            src_path.rename(dst_path)

        return RenameFileResponse(
            success=True,
            old_name=old_name,
            new_name=new_name,
            message=f"Successfully renamed '{old_name}' to '{new_name}'.",
        )
    except PermissionError as pe:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied renaming file: {pe}",
        )
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rename file: {ex}",
        )


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
