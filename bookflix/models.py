from sqlalchemy import Column, String, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    borrowed_books = relationship("Book", back_populates="borrowed_by")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(collation="NOCASE"), unique=True, nullable=False)
    books = relationship("Book", back_populates="category")


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String, unique=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    cover_url = Column(String)
    borrowed_by_id = Column(Integer, ForeignKey("students.id"))
    borrowed_by = relationship("Student", back_populates="borrowed_books")
    borrowed_time = Column(Float)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", back_populates="books")
