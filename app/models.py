## DEFINES the database model structure.This is where we define the database tables and their columns.

from sqlalchemy import String #String tells SQLAlchemy that a database column should store text.
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
#DecBase: gives us SQLAlchemy's base class for defining database models.
#Mapped: SQLAlchemy's way to say This Python attribute is mapped to a database column.
#mapped_column: actually gives us the database-column configuratio
from datetime import datetime

class Base(DeclarativeBase):  #it inherits from SQLAlchemy’s DeclarativeBase
    pass
#“All my models will be children of this one root class -> Base.”
#It doesn’t do anything by itself, but it’s the registry SQLAlchemy uses to know which tables to create.

class URL(Base): #URL is a SQLAlchemy database model.
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(primary_key=True)
    original_url: Mapped[str] = mapped_column(String, nullable=False)
    short_code: Mapped[str] = mapped_column(
        String(6),
        unique=True,
        nullable=False
    )
    click_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False
    )

    last_accessed_at: Mapped[datetime | None] = mapped_column(
        nullable=True
    )  # None? Because a newly created URL hasn't been accessed yet


class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"

    id: Mapped[int] = mapped_column(primary_key=True)

    #client's Idempotency-Key
    key: Mapped[str] = mapped_column( 
        String(255),  # VARCHAR(255) in PostgreSQL
        unique=True,
        nullable=False
    )

    short_code: Mapped[str] = mapped_column(
        String(6),
        nullable=False
    )

    request_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False
    ) #A SHA-256 hash of the request data. SHA-256 produces a 64-character hexadecimal string