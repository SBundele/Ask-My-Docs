import pytest
from sqlalchemy import text

from app.db import SessionLocal, init_db
from app.store import add_chunk, search_similar


def make_vector(x, y):
    """A fake 384-number address. Only the first two numbers matter."""
    return [x, y] + [0.0] * 382


@pytest.fixture
def session():
    init_db()
    s = SessionLocal()
    s.execute(text("TRUNCATE TABLE chunks RESTART IDENTITY"))
    s.commit()
    yield s
    s.close()


def test_search_returns_closest_first(session):
    add_chunk(session, "pets.txt", "Cats say meow", make_vector(1, 0))
    add_chunk(session, "pets.txt", "Dogs say woof", make_vector(0, 1))
    add_chunk(session, "space.txt", "The sun is a star", make_vector(-1, 0))

    results = search_similar(session, make_vector(0.9, 0.1), limit=2)

    assert len(results) == 2
    assert results[0].content == "Cats say meow"
    assert results[1].content == "Dogs say woof"