import pytest
from fastapi.testclient import TestClient
from ent.web.server import app, IDE_DIST_DIR

client = TestClient(app)


def test_api_version():
    response = client.get("/api/version")
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "ENT"
    assert data["version"] == "0.1.0"


def test_api_examples():
    response = client.get("/api/examples")
    assert response.status_code == 200
    examples = response.json()
    assert "hello.ent" in examples
    assert "variables.ent" in examples
    assert "website.ent" in examples


def test_api_run_valid_code():
    source = '[\n    say("Hello from API")\n]'
    response = client.post("/api/run", json={"source": source})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Hello from API" in data["output"]
    assert data["error"] is None


def test_api_run_syntax_error():
    source = 'say("No outer brackets")'
    response = client.post("/api/run", json={"source": source})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["error"] is not None
    assert data["error"]["category"] == "Syntax Error"


def test_api_check_valid():
    source = '[\n    remember(x = 10)\n    say(x)\n]'
    response = client.post("/api/check", json={"source": source})
    assert response.status_code == 200
    assert response.json()["valid"] is True


def test_api_check_invalid():
    source = '[\n    say("unclosed string\n]'
    response = client.post("/api/check", json={"source": source})
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert data["error"]["category"] == "Lexical Error"


def test_api_build_website():
    source = '[\n    page(title = "API Site") [\n        heading("Hello")\n    ]\n]'
    response = client.post("/api/build", json={"source": source})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["title"] == "API Site"
    assert "<h1>Hello</h1>" in data["html"]


def test_serve_ide_frontend():
    if not (IDE_DIST_DIR / "index.html").exists():
        pytest.skip("IDE dist not built; run 'npm --prefix ide run build' to test static frontend serving.")
    response = client.get("/")
    assert response.status_code == 200
    assert "ENT Studio" in response.text
    assert '<div id="root">' in response.text
