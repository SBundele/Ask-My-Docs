from llama_index.core.llms import MockLLM
from llama_index.core.schema import NodeWithScore, TextNode

from app import rag


def make_node(text, score, source="sample.txt"):
    return NodeWithScore(
        node=TextNode(text=text, metadata={"source": source}),
        score=score,
    )


class FakeRetriever:
    def __init__(self, nodes):
        self.nodes = nodes

    def retrieve(self, question):
        return self.nodes


class FakeIndex:
    def __init__(self, nodes):
        self.nodes = nodes

    def as_retriever(self, similarity_top_k=3):
        return FakeRetriever(self.nodes)


def test_retrieve_drops_weak_matches(monkeypatch):
    strong = make_node("Zorblax fears vacuum cleaners", score=0.9)
    weak = make_node("Something unrelated", score=0.05)
    monkeypatch.setattr(rag, "get_index", lambda: FakeIndex([strong, weak]))

    results = rag.retrieve("What scares Zorblax?")

    assert results == [strong]


def test_ask_says_no_answer_and_never_calls_the_ai(monkeypatch):
    monkeypatch.setattr(rag, "retrieve", lambda question, top_k=3: [])

    def explode():
        raise AssertionError("The AI should not be called when nothing was found")

    monkeypatch.setattr(rag, "get_llm", explode)

    result = rag.ask("What is the capital of France?")

    assert result == {"answer": rag.NO_ANSWER, "sources": []}


def test_ask_uses_fake_ai_when_pages_are_found(monkeypatch):
    node = make_node("Zorblax is afraid of vacuum cleaners.", score=0.9)
    monkeypatch.setattr(rag, "retrieve", lambda question, top_k=3: [node])
    monkeypatch.setattr(rag, "get_llm", lambda: MockLLM())  # a pretend Groq

    result = rag.ask("What is Zorblax afraid of?")

    assert result["answer"] != rag.NO_ANSWER
    assert result["sources"][0]["source"] == "sample.txt"
    assert result["sources"][0]["score"] == 0.9