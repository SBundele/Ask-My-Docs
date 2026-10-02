from functools import lru_cache

from llama_index.core import Document, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core import Document, VectorStoreIndex, get_response_synthesizer
from sqlalchemy.engine import make_url

from app.config import DATABASE_URL, GROQ_API_KEY, GROQ_MODEL
from app.models import EMBEDDING_DIM

EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
TABLE_NAME = "askdocs"  # LlamaIndex will store it as "data_askdocs"
MIN_SCORE = 0.25  # pages scoring lower than this are "not really about the question"
NO_ANSWER = "I couldn't find anything about that in your documents."


@lru_cache
def get_embed_model():
    """The meaning machine. Runs on YOUR computer (first run downloads it)."""
    return HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)


@lru_cache
def get_llm():
    """The answer writer. Lives in the Groq cloud."""
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is missing. Add it to your .env file.")
    return Groq(model=GROQ_MODEL, api_key=GROQ_API_KEY)


@lru_cache
def get_vector_store():
    """The shelf. Same PostgreSQL + pgvector from Phase 2."""
    url = make_url(DATABASE_URL)
    return PGVectorStore.from_params(
        host=url.host,
        port=url.port,
        database=url.database,
        user=url.username,
        password=url.password,
        table_name=TABLE_NAME,
        embed_dim=EMBEDDING_DIM,
    )


def get_index():
    return VectorStoreIndex.from_vector_store(
        vector_store=get_vector_store(),
        embed_model=get_embed_model(),
    )


def ingest_text(text: str, source: str) -> int:
    """Cut text into pieces, give each a meaning-address, shelve them."""
    document = Document(text=text, metadata={"source": source})
    splitter = SentenceSplitter(chunk_size=256, chunk_overlap=30)
    nodes = splitter.get_nodes_from_documents([document])
    get_index().insert_nodes(nodes)
    return len(nodes)


def retrieve(question: str, top_k: int = 3):
    """Fetch the closest pieces, and throw away the ones that aren't close enough."""
    retriever = get_index().as_retriever(similarity_top_k=top_k)
    nodes = retriever.retrieve(question)
    return [n for n in nodes if n.score is not None and n.score >= MIN_SCORE]


def ask(question: str, top_k: int = 3) -> dict:
    """Find the closest pieces; if there are none, say so. Otherwise let Groq answer."""
    nodes = retrieve(question, top_k)
    if not nodes:
        return {"answer": NO_ANSWER, "sources": []}

    synthesizer = get_response_synthesizer(llm=get_llm())
    response = synthesizer.synthesize(question, nodes=nodes)

    sources = [
        {
            "source": item.node.metadata.get("source"),
            "text": item.node.get_content()[:200],
            "score": item.score,
        }
        for item in nodes
    ]
    return {"answer": str(response), "sources": sources}