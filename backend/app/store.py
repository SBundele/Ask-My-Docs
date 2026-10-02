from sqlalchemy import select

from app.models import Chunk


def add_chunk(session, source, content, embedding):
    chunk = Chunk(source=source, content=content, embedding=embedding)
    session.add(chunk)
    session.commit()
    return chunk


def search_similar(session, query_embedding, limit=3):
    stmt = (
        select(Chunk)
        .order_by(Chunk.embedding.cosine_distance(query_embedding))
        .limit(limit)
    )
    return list(session.scalars(stmt))