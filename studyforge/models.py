from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def utcnow() -> datetime:
    return datetime.now(UTC)


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    kind: Mapped[str] = mapped_column(String)  # cert | tool | skill
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class OutlineNode(Base):
    __tablename__ = "outline_nodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("outline_nodes.id"))
    title: Mapped[str] = mapped_column(String)
    weight: Mapped[float] = mapped_column(Float, default=0.0)
    order: Mapped[int] = mapped_column(Integer, default=0)


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    base_url: Mapped[str] = mapped_column(String)
    search_url_pattern: Mapped[str | None] = mapped_column(String, nullable=True)
    adapter: Mapped[str] = mapped_column(String, default="generic")
    origin: Mapped[str] = mapped_column(String, default="curated")  # curated | manual
    tags_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class TopicSourceOverride(Base):
    __tablename__ = "topic_source_overrides"

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"))
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    mode: Mapped[str] = mapped_column(String)  # pin | exclude


class SiteScore(Base):
    __tablename__ = "site_scores"

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"))
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    score: Mapped[float] = mapped_column(Float, default=0.0)
    breakdown_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    selected: Mapped[bool] = mapped_column(Boolean, default=False)


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    url: Mapped[str] = mapped_column(String)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    fetched_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    outline_node_id: Mapped[int | None] = mapped_column(ForeignKey("outline_nodes.id"))
    text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    is_canonical: Mapped[bool] = mapped_column(Boolean, default=False)


class Summary(Base):
    __tablename__ = "summaries"

    id: Mapped[int] = mapped_column(primary_key=True)
    outline_node_id: Mapped[int] = mapped_column(ForeignKey("outline_nodes.id"))
    text: Mapped[str] = mapped_column(Text)
    citations_json: Mapped[str | None] = mapped_column(Text, nullable=True)


class Flashcard(Base):
    __tablename__ = "flashcards"

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"))
    outline_node_id: Mapped[int | None] = mapped_column(ForeignKey("outline_nodes.id"))
    front: Mapped[str] = mapped_column(Text)
    back: Mapped[str] = mapped_column(Text)
    source_chunk_id: Mapped[int | None] = mapped_column(ForeignKey("chunks.id"))
    fsrs_state_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"))
    outline_node_id: Mapped[int | None] = mapped_column(ForeignKey("outline_nodes.id"))
    stem: Mapped[str] = mapped_column(Text)
    choices_json: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_chunk_id: Mapped[int | None] = mapped_column(ForeignKey("chunks.id"))


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"))
    mode: Mapped[str] = mapped_column(String)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    answers_json: Mapped[str | None] = mapped_column(Text, nullable=True)


class Progress(Base):
    __tablename__ = "progress"

    id: Mapped[int] = mapped_column(primary_key=True)
    outline_node_id: Mapped[int] = mapped_column(ForeignKey("outline_nodes.id"))
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
