from typing import Optional

from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from starlette import status

# So Pydantic is the framework that allows us to perform validation on data and
# Base model is used to validate those data variables

app = FastAPI()


# Created a Book Object
class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


class BookRequest(BaseModel):
    id: Optional[int] = Field(title="id is not needed")
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length= 100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1950, lt=2024)

    class Config:
        json_schema_extra = {
            'example': {
                'title': 'A new book',
                'author': 'coding with aditya',
                'description': 'A new description of a book',
                'rating': 5,
                'published_date': 2012
            }
        }


BOOKS = [
    Book(1, 'Computer Science', 'coding with Aditya', 'A very nice book', 5, 2012),
    Book(2, "Be fast with FastAPI", "coding with Aditya", "A great book", 5, 2013),
    Book(3, "Master Endpoints", "coding with Aditya", "An awesome book!", 5, 2014),
    Book(4, "HP1", "Author 1", "Book Description", 2, 2016),
    Book(5, "HP2", "Author 2", "Book Description", 3, 2016),
    Book(6, "HP3", "Author 3", "Book Description", 1, 2014)
]


@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS


# Getting a Single Book
@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book

    # if book id never matches
    raise HTTPException(status_code=404, detail='Item Not Found')

@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_book_by_rating(book_rating: int = Query(gt=0, lt=6)):
    books_to_return = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return


@app.get("/books/publish/", status_code=status.HTTP_200_OK)
async def book_by_published_date(publish_date: int = Query(gt=1950, lt=2024)):
    books_to_return = []
    for book in BOOKS:
        if book.published_date == publish_date:
            books_to_return.append(book)
    return books_to_return


# Here we are creating an object(book) so we have given 201 status.
@app.post("/create_book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    # It returns all the variables in dictionary form
    new_book = Book(**book_request.model_dump()) # instead of model_dump, use dict()
    BOOKS.append(find_book_id(new_book))


def find_book_id(book : Book):
    if len(BOOKS) > 0:
        book.id = BOOKS[-1].id + 1
    else:
        book.id = 1
    return book


# Here we are not creating anything, so we have given 204 status.
@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = book
            book_changed = True

    # If No Book has changed, then raise exception
    if not book_changed:
        raise HTTPException(status_code=404, detail='Book Not Found')


# Here we are not returning, we are just enhancing something so 204 is given.
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id:int):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            book_changed = True
            break

    # If No Book has deleted, then raise exception
    if not book_changed:
        raise HTTPException(status_code=404, detail='Book Not Found')
