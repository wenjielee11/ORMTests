from tortoise import Tortoise, fields, run_async
from tortoise.models import Model
import asyncio
from typing import List, Optional
import time

class Author(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    books = fields.ManyToManyField("models.Book", related_name="authors", through="book_author_link")

class Book(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)

class BookAuthorLink(Model):
    book = fields.ForeignKeyField("models.Book", related_name="author_links")
    author = fields.ForeignKeyField("models.Author", related_name="book_links")

async def init():
    await Tortoise.init(
        db_url='sqlite://tortoisedatabase.db',
        modules={'models': ['__main__']}
    )
    await Tortoise.generate_schemas()

async def create_book(title: str, author_names: List[str]):
  
    authors = await Author.filter(name__in=author_names)
    book = await Book.create(title=title)
    await book.authors.add(*authors)
    result = await get_books()
   
    return book

async def create_author(name: str):

    author = await Author.create(name=name)
    result = await get_authors()


    return author

async def get_books():
    return await Book.all().prefetch_related("authors")

async def get_authors():
    return await Author.all().prefetch_related("books")

async def update_book(book_id: int, new_title: str):

    book = await Book.get(id=book_id)
    book.title = new_title
    await book.save()
    result = await get_books()

    return book

async def update_author(author_id: int, new_name: Optional[str] = None, new_books: Optional[List[str]] = None):
    author = await Author.get(id=author_id)
    if new_name:
        author.name = new_name
    if new_books:
        books = await Book.filter(title__in=new_books)
        await author.books.set(books)
    await author.save()
    result = await get_authors()
    return author

async def delete_book(book_id: int):
    book = await Book.get(id=book_id)
    await book.delete()
    result = await get_books()
   

async def delete_author(author_id: int):
   
    author = await Author.get(id=author_id)
    await author.delete()
    result = await get_authors()
 

async def delete_all_authors_and_books():
    await BookAuthorLink.all().delete()
    await Author.all().delete()
    await Book.all().delete()

# Additional async tasks for demonstration
async def dummy_task(task_name: str, duration: int):

    await asyncio.sleep(duration)


async def main():
    start = time.time()
    await init()
    
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
    books_after_deletion = await get_books()
    authors_after_deletion = await get_authors()

    end = time.time()
    print(f"Tortoise benchmark time: {end - start:.4f} seconds")

# Have to close connection in tortoise. 
run_async(main())
