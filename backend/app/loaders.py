import io
from pypdf import PdfReader


def extract_text(filename: str, data: bytes) -> str:
    """Turn an uploaded file into plain text."""
    name = filename.lower()

    if name.endswith((".txt", ".md")):
        return data.decode("utf-8", errors="ignore")

    if name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(data))
        return "\n".join((page.extract_text() or "") for page in reader.pages)

    raise ValueError(f"Unsupported file type: {filename}")