"""ORM models."""
from datetime import datetime

from sqlalchemy import Table, Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

book_genre = Table(
    "book_genre",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True),
)


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    bio = Column(String(1000), nullable=True)
    country = Column(String(100), nullable=True)

    books = relationship("Book", back_populates="author_rel", cascade="all, delete-orphan")


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)
    isbn = Column(String(20), nullable=True)
    published_year = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_by = relationship("Users", back_populates="books")
    author_rel = relationship("Author", back_populates="books")
    genres = relationship("Genre", secondary=book_genre, back_populates="books")


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    books = relationship("Book", secondary=book_genre, back_populates="genres")


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    books = relationship("Book", back_populates="created_by")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    completed = Column(Boolean, nullable=False, default=False)
