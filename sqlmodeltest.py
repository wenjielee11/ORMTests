from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship, select, delete
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
import asyncio
import time

class BookAuthorLink(SQLModel, table=True):
    book_id: Optional[int] = Field(default=None, foreign_key="book.id", primary_key=True)
    author_id: Optional[int] = Field(default=None, foreign_key="author.id", primary_key=True)

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    authors: List["Author"] = Relationship(back_populates="books", link_model=BookAuthorLink)

class Author(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    books: List[Book] = Relationship(back_populates="authors", link_model=BookAuthorLink)

sqlite_file_name = "sqlmodeldatabase.db"
sqlite_url = f"sqlite+aiosqlite:///{sqlite_file_name}"

engine = create_async_engine(sqlite_url)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def create_book(title: str, author_names: List[str]):
   
    async with AsyncSession(engine) as session:
        book = Book(title=title)
        authors = await session.exec(select(Author).where(Author.name.in_(author_names)))
        book.authors.extend(authors.all())
        session.add(book)
        await session.commit()
        await session.refresh(book)
        result = await get_books()
      
        return book

async def create_author(name: str):
    
    async with AsyncSession(engine) as session:
        author = Author(name=name)
        session.add(author)
        await session.commit()
        await session.refresh(author)
        result = await get_authors()
      
        return author

async def get_books():
    async with AsyncSession(engine) as session:
        result = await session.exec(select(Book))
        return result.all()

async def get_authors():
    async with AsyncSession(engine) as session:
        result = await session.exec(select(Author))
        return result.all()

async def update_book(book_id: int, new_title: str):
 
    async with AsyncSession(engine) as session:
        book = await session.get(Book, book_id)
        if new_title:
            book.title = new_title

        session.add(book)
        await session.commit()
        await session.refresh(book)
        result = await get_books()
   
        return book

async def update_author(author_id: int, new_name: Optional[str] = None, new_books: Optional[List[str]] = None):
    
    async with AsyncSession(engine) as session:
        author = await session.get(Author, author_id)
        if new_name:
            author.name = new_name
        if new_books:
            books = await session.exec(select(Book).where(Book.title.in_(new_books)))
            author.books = books.all()
        session.add(author)
        await session.commit()
        await session.refresh(author)
        result = await get_authors()
  
        return author

async def delete_book(book_id: int):
 
    async with AsyncSession(engine) as session:
        book = await session.get(Book, book_id)
        await session.delete(book)
        await session.commit()
        result = await get_books()


async def delete_author(author_id: int):
  
    async with AsyncSession(engine) as session:
        author = await session.get(Author, author_id)
        await session.delete(author)
        await session.commit()
        result = await get_authors()


async def delete_all_authors_and_books():
    async with AsyncSession(engine) as session:
        await session.exec(delete(BookAuthorLink))  # Delete all entries in the association table first
        await session.exec(delete(Author))  # Delete all authors
        await session.exec(delete(Book))  # Delete all books
        await session.commit()

# Additional async tasks for demonstration
async def dummy_task(task_name: str, duration: int):
  
    await asyncio.sleep(duration)
  

async def main():
    start = time.time()
    await create_db_and_tables()
    
     #Create authors and books first
    await asyncio.gather(
        create_author("Author One"),
        create_author("Author Two"),
        create_book("Book One", ["Author One"]),
        create_book("Book Two", ["Author Two"]),
        dummy_task("Task 1", 1)
    )

    await asyncio.gather(
        dummy_task("Task 2", 2),
        update_book(1, "Updated Book One"),
    )

    # Run dummy tasks and delete operations
    await asyncio.gather(
       
        dummy_task("Task 3", 2),
        delete_book(2),
    )

    # Delete all authors and books
    await delete_all_authors_and_books()

    # Verify deletion
    await delete_all_authors_and_books()
    books_after_deletion = await get_books()
    authors_after_deletion = await get_authors()

    end = time.time()
    print(f"SQLModel benchmark time: {end - start:.4f} seconds")

import asyncio
asyncio.run(main())
