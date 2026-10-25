"""
Structured error types and diagnostic formatting for ENT.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Any, Dict


@dataclass
class SourceLocation:
    file: str = "<stdin>"
    line: int = 1
    column: int = 1

    def __str__(self) -> str:
        return f"{self.file}:{self.line}:{self.column}"


class EntError(Exception):
    """Base class for all ENT diagnostics and errors."""

    def __init__(
        self,
        category: str,
        message: str,
        location: Optional[SourceLocation] = None,
        source_line: Optional[str] = None,
        suggestion: Optional[str] = None,
    ):
        super().__init__(message)
        self.category = category
        self.message = message
        self.location = location or SourceLocation()
        self.source_line = source_line
        self.suggestion = suggestion

    def format_diagnostic(self) -> str:
        """Render a beginner-friendly, clean diagnostic message."""
        lines = [
            f"[{self.category}] in {self.location}:",
            f"  Error: {self.message}",
        ]
        if self.source_line is not None and self.source_line.strip():
            lines.append(f"    {self.source_line}")
            # Align caret
            col = max(1, self.location.column)
            # Take indentation of source line into account
            pointer = " " * (col - 1) + "^"
            lines.append(f"    {pointer}")
        if self.suggestion:
            lines.append(f"  Tip: {self.suggestion}")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON API responses."""
        return {
            "category": self.category,
            "message": self.message,
            "file": self.location.file,
            "line": self.location.line,
            "column": self.location.column,
            "source_line": self.source_line,
            "suggestion": self.suggestion,
            "formatted": self.format_diagnostic(),
        }

    def __str__(self) -> str:
        return self.format_diagnostic()


class EntLexicalError(EntError):
    def __init__(
        self,
        message: str,
        location: Optional[SourceLocation] = None,
        source_line: Optional[str] = None,
        suggestion: Optional[str] = None,
    ):
        super().__init__("Lexical Error", message, location, source_line, suggestion)


class EntSyntaxError(EntError):
    def __init__(
        self,
        message: str,
        location: Optional[SourceLocation] = None,
        source_line: Optional[str] = None,
        suggestion: Optional[str] = None,
    ):
        super().__init__("Syntax Error", message, location, source_line, suggestion)


class EntRuntimeError(EntError):
    def __init__(
        self,
        message: str,
        location: Optional[SourceLocation] = None,
        source_line: Optional[str] = None,
        suggestion: Optional[str] = None,
    ):
        super().__init__("Runtime Error", message, location, source_line, suggestion)


class EntLimitExceededError(EntRuntimeError):
    def __init__(
        self,
        message: str,
        location: Optional[SourceLocation] = None,
        source_line: Optional[str] = None,
        suggestion: Optional[str] = None,
    ):
        super().__init__(
            message=message,
            location=location,
            source_line=source_line,
            suggestion=suggestion or "Consider optimizing your loop or increasing the step limit.",
        )
        self.category = "Limit Exceeded"


class EntBuildError(EntError):
    def __init__(
        self,
        message: str,
        location: Optional[SourceLocation] = None,
        source_line: Optional[str] = None,
        suggestion: Optional[str] = None,
    ):
        super().__init__("Build Error", message, location, source_line, suggestion)
