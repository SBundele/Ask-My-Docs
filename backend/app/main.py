from fastapi import FastAPI

app = FastAPI(title="Ask My Docs")


@app.get("/health")
def health():
    return {"status": "ok"}