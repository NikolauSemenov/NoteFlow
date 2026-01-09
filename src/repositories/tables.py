from sqlalchemy import (
    Table,
    MetaData,
    Column,
    Text,
    String,
    DateTime,
    func,
    Boolean,
    Integer,
    ForeignKey,
    text,
    UniqueConstraint,
)

metadata = MetaData()

Note = Table(
    "notes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(255)),
    Column("content", Text()),
    Column("user_full_name", String(), nullable=False),
    Column("user_id", Integer(), nullable=False),
    Column("is_active", Boolean(), server_default=text("true"), nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
    Column("updated_at", DateTime(timezone=True), onupdate=func.now(), nullable=True),
)

Like = Table(
    "likes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer(), nullable=False),
    Column("note_id", Integer(), ForeignKey("notes.id"), nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
    UniqueConstraint("user_id", "note_id", name="uq_user_note_like"),
)

Comment = Table(
    "comments",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("text", String(), nullable=False),
    Column("user_id", Integer(), nullable=False),
    Column("user_full_name", String(), nullable=False),
    Column("note_id", Integer(), ForeignKey("notes.id"), nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
)
