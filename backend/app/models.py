from pgvector.sqlalchemy import Vector
from sqlalchemy import Integer, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 makes 384 numbers per text


class Base(DeclarativeBase):
    pass


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(Text)    # which file it came from
    content: Mapped[str] = mapped_column(Text)   # the actual text piece
    embedding = mapped_column(Vector(EMBEDDING_DIM))  # its meaning-address