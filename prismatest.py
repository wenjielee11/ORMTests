from prisma import Prisma
from typing import List, Optional
import asyncio
import time

db = Prisma()

class Book:
    id: Optional[int]
    title: str
    authors: List["Author"]

class Author:
    id: Optional[int]
    name: str
    books: List[Book]


async def create_book(title: str, author_names: List[str]):
    
    authors = await db.author.find_many(where={'name': {'in': author_names}})
    book = await db.book.create(
        data={
            'title': title,
            'authors': {
                'create': [{'author': {'connect': {'id': author.id}}} for author in authors]
            }
        }
    )
    # print("Books after create book: ", await get_books())
    return book

async def create_author(name: str):
    
    author = await db.author.create(data={'name': name})
    # print("Author after create author: ", await get_authors())
    return author

async def get_books():
  
    books = await db.book.find_many(include={'authors': True})
 
    return books

async def get_authors():
 
    authors = await db.author.find_many(include={'books': True})
   
    return authors

async def update_book(book_id: int, new_title: str):
   
    book = await db.book.update(
        where={'id': book_id},
        data={'title': new_title}
    )
    # print("book after update: ", await get_books())
    return book

async def update_author(author_id: int, new_name: Optional[str] = None, new_books: Optional[List[str]] = None):
    
    update_data = {}
    if new_name:
        update_data['name'] = new_name
    if new_books:
        books = await db.book.find_many(where={'title': {'in': new_books}})
        update_data['books'] = {'set': [{'book': {'connect': {'id': book.id}}} for book in books]}
    author = await db.author.update(
        where={'id': author_id},
        data=update_data
    )
    # print("author after update: ", await get_authors())
    return author

async def delete_book(book_id: int):
   
    await db.book.delete(where={'id': book_id})
    # print("book after delete: ", await get_books())
    

async def delete_author(author_id: int):
    
    await db.author.delete(where={'id': author_id})
    # print("author after delete: ", await get_authors())
  

async def delete_all_authors_and_books():
  
    await db.bookauthorlink.delete_many()
    await db.author.delete_many()
    await db.book.delete_many()
   

async def dummy_task(task_name: str, duration: int):
    await asyncio.sleep(duration)

async def main():
    start = time.time()
    await db.connect()
    await asyncio.gather(
        create_author("Author One"),
        create_author("Author Two"),
        create_book("Book One", ["Author One"]),
        dummy_task("Task 1", 1)
    )

    await asyncio.gather(
        create_book("Book Two", ["Author Two"]),
        dummy_task("Task 2", 2),
        update_book(1, "Updated Book One"),
    )

    await asyncio.gather(
        dummy_task("Task 3", 2),
        delete_book(2),
    )

    await delete_all_authors_and_books()

    books_after_deletion = await get_books()
    authors_after_deletion = await get_authors()

    end = time.time()
    await db.disconnect()

asyncio.run(main())
