from fastapi.testclient import TestClient

from app import rag
from app.main import app

client = TestClient(app)


# ---------- Upload slot: POST /documents ----------

def test_upload_text_file_works(monkeypatch):
    calls = []

    def fake_ingest(text, source):
        calls.append((text, source))
        return 2  # pretend we made 2 pieces

    monkeypatch.setattr(rag, "ingest_text", fake_ingest)

    response = client.post(
        "/documents",
        files={"file": ("notes.txt", b"hello world", "text/plain")},
    )

    assert response.status_code == 200
    assert response.json() == {"filename": "notes.txt", "chunks": 2}
    assert calls == [("hello world", "notes.txt")]


def test_upload_rejects_unknown_file_type():
    response = client.post(
        "/documents",
        files={"file": ("virus.exe", b"data", "application/octet-stream")},
    )
    assert response.status_code == 400


def test_upload_rejects_empty_file():
    response = client.post(
        "/documents",
        files={"file": ("empty.txt", b"   ", "text/plain")},
    )
    assert response.status_code == 400


# ---------- Question desk: POST /ask ----------

def test_ask_returns_the_answer(monkeypatch):
    fake_result = {
        "answer": "Vacuum cleaners.",
        "sources": [{"source": "sample.txt", "text": "...", "score": 0.9}],
    }
    monkeypatch.setattr(rag, "ask", lambda question: fake_result)
    response = client.post("/ask", json={"question": "What scares Zorblax?"})

    assert response.status_code == 200
    assert response.json() == fake_result


def test_ask_rejects_empty_question():
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 422


def test_ask_gives_503_when_ai_is_not_set_up(monkeypatch):
    def broken(question):
        raise RuntimeError("GROQ_API_KEY is missing. Add it to your .env file.")

    monkeypatch.setattr(rag, "ask", broken)
    response = client.post("/ask", json={"question": "Hi?"})

    assert response.status_code == 503