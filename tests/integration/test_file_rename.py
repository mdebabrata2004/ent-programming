import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from ent.web.server import app

client = TestClient(app)


@pytest.fixture
def temp_workspace(tmp_path: Path, monkeypatch):
    """Sets a clean temporary workspace for file rename tests."""
    ws = tmp_path / "workspace"
    ws.mkdir()
    monkeypatch.setenv("ENT_WORKSPACE_DIR", str(ws))
    return ws


def test_1_successful_rename(temp_workspace: Path):
    src = temp_workspace / "alpha.ent"
    src.write_text('[ say("Alpha") ]', encoding="utf-8")

    response = client.post("/api/files/rename", json={"old_name": "alpha.ent", "new_name": "beta.ent"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["old_name"] == "alpha.ent"
    assert data["new_name"] == "beta.ent"

    assert not (temp_workspace / "alpha.ent").exists()
    assert (temp_workspace / "beta.ent").exists()
    assert (temp_workspace / "beta.ent").read_text(encoding="utf-8") == '[ say("Alpha") ]'


def test_2_rename_preserves_content(temp_workspace: Path):
    src = temp_workspace / "script.ent"
    content = '[\n    remember(x = 100)\n    say(x)\n]'
    src.write_text(content, encoding="utf-8")

    response = client.post("/api/files/rename", json={"old_name": "script.ent", "new_name": "renamed_script.ent"})
    assert response.status_code == 200
    assert (temp_workspace / "renamed_script.ent").read_text(encoding="utf-8") == content


def test_3_duplicate_destination_rejected(temp_workspace: Path):
    (temp_workspace / "file1.ent").write_text("1", encoding="utf-8")
    (temp_workspace / "file2.ent").write_text("2", encoding="utf-8")

    response = client.post("/api/files/rename", json={"old_name": "file1.ent", "new_name": "file2.ent"})
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]
    # Verify file2 content was not overwritten
    assert (temp_workspace / "file2.ent").read_text(encoding="utf-8") == "2"


def test_4_empty_filename_rejected(temp_workspace: Path):
    response = client.post("/api/files/rename", json={"old_name": "   ", "new_name": "valid.ent"})
    assert response.status_code == 400 or response.status_code == 422


def test_5_invalid_characters_rejected(temp_workspace: Path):
    for bad in ["bad*name.ent", "bad?name.ent", "bad<name>.ent", "bad|name.ent"]:
        response = client.post("/api/files/rename", json={"old_name": "test.ent", "new_name": bad})
        assert response.status_code == 400
        assert "invalid characters" in response.json()["detail"].lower()


def test_6_path_traversal_rejected(temp_workspace: Path):
    traversal_payloads = [
        {"old_name": "../secret.ent", "new_name": "safe.ent"},
        {"old_name": "safe.ent", "new_name": "../secret.ent"},
        {"old_name": "..\\secret.ent", "new_name": "safe.ent"},
        {"old_name": "/etc/passwd.ent", "new_name": "safe.ent"},
    ]
    for payload in traversal_payloads:
        response = client.post("/api/files/rename", json=payload)
        assert response.status_code == 400
        assert "path traversal" in response.json()["detail"].lower() or "forbidden" in response.json()["detail"].lower()


def test_7_missing_source_file_404(temp_workspace: Path):
    response = client.post("/api/files/rename", json={"old_name": "nonexistent.ent", "new_name": "new.ent"})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_8_case_only_rename(temp_workspace: Path):
    src = temp_workspace / "lowercase.ent"
    src.write_text("content", encoding="utf-8")

    response = client.post("/api/files/rename", json={"old_name": "lowercase.ent", "new_name": "LowerCase.ent"})
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_9_unsupported_extension_rejected(temp_workspace: Path):
    (temp_workspace / "script.ent").write_text("test", encoding="utf-8")
    for bad_ext in ["script.py", "script.exe", "script.txt", "script"]:
        response = client.post("/api/files/rename", json={"old_name": "script.ent", "new_name": bad_ext})
        assert response.status_code == 400
        assert "only '.ent' files" in response.json()["detail"].lower()


def test_10_leading_trailing_spaces_rejected(temp_workspace: Path):
    response = client.post("/api/files/rename", json={"old_name": "test.ent", "new_name": " bad.ent"})
    assert response.status_code == 400


def test_11_explorer_list_updated_after_rename(temp_workspace: Path):
    (temp_workspace / "old_site.ent").write_text("page", encoding="utf-8")

    # Before rename
    list_before = client.get("/api/examples").json()
    assert "old_site.ent" in list_before

    # Rename
    client.post("/api/files/rename", json={"old_name": "old_site.ent", "new_name": "new_site.ent"})

    # After rename
    list_after = client.get("/api/examples").json()
    assert "old_site.ent" not in list_after
    assert "new_site.ent" in list_after


def test_12_permission_error_handling(temp_workspace: Path, monkeypatch):
    (temp_workspace / "locked.ent").write_text("locked", encoding="utf-8")

    def mock_rename(*args, **kwargs):
        raise PermissionError("Access denied by OS")

    monkeypatch.setattr(Path, "rename", mock_rename)

    response = client.post("/api/files/rename", json={"old_name": "locked.ent", "new_name": "unlocked.ent"})
    assert response.status_code == 403
    assert "permission denied" in response.json()["detail"].lower()


def test_13_os_error_handling(temp_workspace: Path, monkeypatch):
    (temp_workspace / "err.ent").write_text("test", encoding="utf-8")

    def mock_rename(*args, **kwargs):
        raise OSError("Disk I/O error")

    monkeypatch.setattr(Path, "rename", mock_rename)

    response = client.post("/api/files/rename", json={"old_name": "err.ent", "new_name": "new_err.ent"})
    assert response.status_code == 500
    assert "failed to rename" in response.json()["detail"].lower()


def test_14_existing_destination_not_overwritten(temp_workspace: Path):
    (temp_workspace / "original.ent").write_text("ORIGINAL", encoding="utf-8")
    (temp_workspace / "target.ent").write_text("TARGET", encoding="utf-8")

    response = client.post("/api/files/rename", json={"old_name": "original.ent", "new_name": "target.ent"})
    assert response.status_code == 409
    assert (temp_workspace / "original.ent").read_text(encoding="utf-8") == "ORIGINAL"
    assert (temp_workspace / "target.ent").read_text(encoding="utf-8") == "TARGET"


def test_15_rename_validation_without_trusting_client(temp_workspace: Path):
    # Test boundary check when client tries to trick the server
    (temp_workspace / "normal.ent").write_text("code", encoding="utf-8")
    response = client.post("/api/files/rename", json={"old_name": "normal.ent", "new_name": "subdir/nested.ent"})
    assert response.status_code == 400
