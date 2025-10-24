from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.responses import FileResponse
import uvicorn
from pydantic import BaseModel
from typing import Annotated
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


app = FastAPI()

# books = [
#     {
#         "id":1,
#         "title": "Вы напугали деда",
#         "author": "Мастер 2001"
#     },
#     {
#         "id":2,
#         "title": "Арахнофоб",
#         "author": "Паук Дима"
#     },
# ]

# @app.get(
#         "/books",
#         tags=["Книги"],
#         summary="Получить все книги"
# )
# def read_books():
#     return books

# @app.get(
#         "/books/{book_id}",
#         tags=["Книги"],
#         summary="Получить конкретную книжку"
# )
# def get_book(book_id: int):
#     for book in books:
#         if book["id"] == book_id:
#             return book
#         raise HTTPException(status_code=404, detail="Книга не найдена")


# class NewBook(BaseModel):
#     title: str
#     author: str

# @app.post('/books')
# def create_book(new_book: NewBook):
#     books.append({
#         "id": len(books) + 1,
#         "title": new_book.title,
#         "author": new_book.author,
#     })
#     return {"Ok": True}

engine = create_async_engine('sqlite+aiosqlite:///books.db')

new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]


class Base(DeclarativeBase):
    pass

class BookModel(Base):
    __tablename__  = 'books'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author: Mapped[str]

@app.post('/setup_database')
async def setup_databases():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    return {'Ok', True}

class BookAddSchema(BaseModel):
    title: str
    author: str

class BookSchema(BookAddSchema):
    id: int

@app.post('/books')
async def add_book(data: BookAddSchema, session: SessionDep):
    new_book = BookModel(
        title=data.title,
        author=data.author
    )


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)