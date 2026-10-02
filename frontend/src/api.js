const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

async function handle(response) {
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (typeof body.detail === "string") message = body.detail;
    } catch {
      // the error had no readable message, keep the default one
    }
    throw new Error(message);
  }
  return response.json();
}

export async function uploadDocument(file) {
  const form = new FormData();
  form.append("file", file);
  return handle(
    await fetch(`${API_URL}/documents`, { method: "POST", body: form }),
  );
}

export async function askQuestion(question) {
  return handle(
    await fetch(`${API_URL}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    }),
  );
}
